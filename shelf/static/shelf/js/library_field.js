$(function() {
    /**
     * Library browsing & file / picture selection
     */

    // transforms <a> links to XHR requests loaded in modal dialogs
    $(document).on('click', '.modal a.xhr_link', function(e) {
        e.preventDefault();
        $(this).closest('.modal').load($(this).attr('href'));
    });

    // selects a file in modal popup
    $(document).on('click', '.modal .modal_file_selector .modal_file_element', function(e) {
        e.preventDefault();
        e.stopPropagation();

        var selector = $(this).closest('.modal_file_selector');
        var validator = selector.find('.modal_file_validate').first();

        console.log("Selecting: selector = ", selector, " validator = ", validator);

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

    // validates file selection in modal popup
    $(document).on('click', '.modal .modal_file_selector .modal_file_validate', function(e) {
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

    // list of documents to upload
    var documents = [];

    // updates upload progress for a specific document
    function updateProgressBar(scope, el, loaded, total)
    {
        var nb_completed;
        var percent = (loaded * 100.0) / total;

        var progress_container = el.find('.progress').first();
        var progress_bar = el.find('.progress-bar').first();
        var check_icon = el.find('a.del i').first();

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

        total = 0;
        loaded = 0;
        nb_completed = 0;

        for (var i in documents)
        {
            if (documents[i]['size'] == documents[i]['uploaded']) {
                nb_completed++;
            }

            total += documents[i]['size'];
            loaded += documents[i]['uploaded'];
        }

        if (total > 0 && loaded == total) {
            feedback_message(scope, 'done');
        }
        else {
            feedback_message(scope, 'uploading', documents.length - nb_completed);
        }
    }

    // starts uploading a list of files
    function upload(scope, files)
    {
        for (var j = 0; j < files.length; j++)
        {
            // Only processes image files
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
            el.find('.file-size-text').first().text(humanize.filesize({number: f.size}))

            documents.push({
                'file': f.name,
                'size': f.size,
                'uploaded': 0,
                'type': f.type,
                'el': el,
                'f': f
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
                                    if (documents[i]['f'] == f) {
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

    // notifies the user on the upload status
    function feedback_message(scope, message, arg) {
        var el = scope.find('.modal_upload_feedback').first();
        var msg = el.data('msg-' + message);

        if (typeof arg != undefined) {
            msg = msg.replace('%d', arg);
        }

        el.text(msg);
    }

    // selects files to upload by pressing a button
    $(document).on('click', '.modal .modal_upload_button', function(e) {
        var scope = $(this).closest('.modal');

        $('#jquery_file_fake_selector').click();
        $('#jquery_file_fake_selector').one('change', function() {
            upload(scope, this.files);
            $(this).val('');
        });
    });

    // selects files to upload by drag-and-drop
    $(document).on('drop', '.modal .modal_upload_dropzone', function(e) {
        var scope = $(this).closest('.modal');
        e = e.originalEvent;

        if (!e.dataTransfer || !e.dataTransfer.files.length) {
            return;
        }

        upload(scope, e.dataTransfer.files);
    });

    // enables drag-and-drop support by calling event.preventDefault()
    // for "dragover" and "drop" events;
    // the call is implicitely done with "return false" (thanks to jQuery)
    $(document).on('dragover drop', '.modal .modal_upload_dropzone', function(e) {
        return false;
    });

    // displayes different styles for the dropzone for rejected and accepted elements
    $(document).on('dragleave drop', '.modal .modal_upload_dropzone', function(e) {
        this.dragenter_level -= 1;

        if (e.target != this) {
            return;
        }

        if (!this.dragenter_level) {
            $(this).removeClass('modalBiblio--zonedrop--ko').removeClass('modalBiblio--zonedrop--ok');
        }
    });

    $(document).on('dragenter', '.modal .modal_upload_dropzone', function(e) {
        var e = e.originalEvent;
        var data = e.dataTransfer;
        var data_ok = false;

        if (typeof this.dragenter_level === "undefined") {
            this.dragenter_level = 0;
        }

        this.dragenter_level += 1;

        for (var i = 0; i < data.items.length; i += 1) {
            var item = data.items[i];

            if (item.kind === "file") {
                data_ok = true;
            }
        }

        if (data_ok) {
            $(this).addClass('modalBiblio--zonedrop--ok').removeClass('modalBiblio--zonedrop--ko');
        }
        else {
            $(this).addClass('modalBiblio--zonedrop--ko').removeClass('modalBiblio--zonedrop--ok');
        }
    });
});