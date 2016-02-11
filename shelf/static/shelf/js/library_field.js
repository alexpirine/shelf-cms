$(function() {
    // transform <a> links to XHR requests in modal dialogs
    $('.modal').on('click', 'a.xhr_link', function(e) {
        e.preventDefault();
        $(this).closest('.modal').load($(this).attr('href'));
    });
    
    // selects file in a modal popup
    $('.modal').on('click', '.modal_file_selector .modal_file_element', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var selector = $(this).closest('.modal_file_selector');
        var validator = selector.find('.modal_file_validate').first();
        
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
            
            if (!validator.hasClass('disabled')) {
                validator.addClass('disabled');
            }
        }
        else {
            selector.find('.modal_file_element.selected').removeClass('selected');
            $(this).addClass('selected');
            
            if (validator.hasClass('disabled')) {
                validator.removeClass('disabled');
            }
            validator.data('url', $(this).data('url'));
        }
    });
    
    // validates file selection in a modal popup
    $('.modal').on('click', '.modal_file_selector .modal_file_validate', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var url = $(this).data('url');
        var modal = $(this).closest('.modal_file_selector').closest('.modal');
        
        if ($(this).hasClass('disabled') || !url) {
            return;
        }
        
        if (modal.data('val-target')) {
            $(modal.data('val-target')).val(url);
        }
        
        if (modal.data('src-target')) {
            $(modal.data('src-target')).attr('src', url);
        }
        
        modal.modal('hide');
    });
    
    /**
     * Upload
     */
    
    var documents = []
    
    function updateProgressBar(scope, el, loaded, total)
    {
        var percent = (loaded * 100.0) / total;
        
        progress_container = el.find('.progress').first();
        progress_bar = el.find('.progress-bar').first();
        check_icon = el.find('a.del i').first();
        
        progress_bar.width(percent + '%');
        progress_bar.attr({'aria-valuenow': loaded, 'aria-valuemax': total});
        
        if (percent > 95 && progress_bar.hasClass('progress-bar-warning')) {
            progress_bar.addClass('progress-bar-success');
            progress_bar.removeClass('progress-bar-warning');
        }
        
        if (loaded == total) {
            check_icon.removeClass('fa-times');
            check_icon.addClass('fa-check');
            el.removeClass('actif');
        }
        
        var total = 0;
        var loaded = 0;
        var nb_complete = 0;
        
        for (var i in documents)
        {
            if (documents[i]['size'] == documents[i]['uploaded']) {
                nb_complete++;
            }
            
            total += documents[i]['size'];
            loaded += documents[i]['uploaded'];
        }
        
        if (total > 0 && loaded == total) {
            feedback_message(scope, 'done');
        }
        else {
            feedback_message(scope, 'uploading', documents.length - nb_complete);
        }
    }

    function upload(scope, files)
    {
        for (var j = 0; j < files.length; j++)
        {
            // Only process image files.
            /*if (!f.type.match('image/jpeg')) {
               alert('The file must be a jpeg image') ;
               return false ;
            }*/
            
            var reader = new FileReader();
            var f = files[j];
            
            var item = scope.find('.example-file').html();
            
            scope.find('.modalBiblio--queue').prepend(item);
            var el = scope.find('.modalBiblio--queue .modalBiblio--queue-fichier').first();
            el.find('.upload_file_name').html(f.name);
            
            documents.push({
                'file': f.name,
                'size': f.size,
                'uploaded': 0,
                'type': f.type,
                'el': el
            });
            
            reader.onload = (function(f) {
                return function (evt) {
                    var pic = {};
                    pic.file = evt.target.result.split(',')[1];
                    pic.path = scope.find('.modal_upload_dropzone').data('upload-dir');
                    pic.name = f.name;
                    
                    var str = jQuery.param(pic);
                    var total_upload_size = 0;
                    
                    $.ajax({
                        type: 'POST',
                        url: scope.find('.modal_upload_dropzone').data('async-upload-url'),
                        data: str,
                        xhr: function() {
                            var xhr = new window.XMLHttpRequest();
                            xhr.upload.addEventListener("progress", function(e) {
                                if (!e.lengthComputable) {
                                    return;
                                }
                                
                                for (var i in documents)
                                {
                                    if (documents[i]['file'] == f.name) {
                                        documents[i]['uploaded'] = e.loaded;
                                        documents[i]['size'] = e.total;
                                        updateProgressBar(scope, documents[i]['el'], documents[i]['uploaded'], documents[i]['size']);
                                        break;
                                    }
                                }
                            }, false);
                            
                            return xhr;
                        },
                        success: function(data) {
                            for (var i in documents)
                            {
                                if (documents[i]['file'] == f.name) {
                                    documents[i]['uploaded'] = documents[i]['size'];
                                    updateProgressBar(scope, documents[i]['el'], documents[i]['uploaded'], documents[i]['size']);
                                    break;
                                }
                            }
                        }
                    });
                };
            })(files[j]);
          
            reader.readAsDataURL(f);
        }
    }
    
    function feedback_message(scope, message, arg) {
        var el = scope.find('.modal_upload_feedback').first();
        var msg = el.data('msg-' + message);
        
        if (typeof arg != undefined) {
            msg = msg.replace('%d', arg);
        }
        
        el.text(msg);
    }
    
    $('.modal').on('click', '.modal_upload_button', function(e) {
        var scope = $(this).closest('.modal');
        
        $('#jquery_file_fake_selector').click();
        $('#jquery_file_fake_selector').one('change', function() {
            upload(scope, this.files);
            $(this).val('');
        });
    });
    
    $('.modal').on('dragover drop', '.modal_upload_dropzone', function(e){
        e.preventDefault();
        e.stopPropagation();
    });
    
    $('.modal').on('drop', '.modal_upload_dropzone', function(e) {
        var scope = $(this).closest('.modal');
        
        if (!e.originalEvent.dataTransfer || !e.originalEvent.dataTransfer.files.length) {
            return;
        }
        
        upload(scope, e.originalEvent.dataTransfer.files);
    });
});