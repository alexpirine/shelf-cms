// Copyright (c) Alexandre Syenchuk (alexpirine), 2016
// Licensed under the GPL version 2.0 license
// See http://www.gnu.org/licenses/old-licenses/gpl-2.0.html

jQuery.fn.setHover = function() {
    var e = document.createEvent('MouseEvents');
    e.initEvent('mousedown', true, false);
    $(this).addClass('hover').get(0).dispatchEvent(e);

    return $(this);
};

jQuery.fn.unsetHover = function() {
    var e = document.createEvent('MouseEvents');
    e.initEvent('mouseout', true, false);
    $(this).removeClass('hover').get(0).dispatchEvent(e);

    return $(this);
};

jQuery.fn.file = function(allowed_types, onready_cb, onload_cb) {
    var element = $(this);
    var fr = new FileReader();
    var el = $(this).get(0);

    if (!el) {
        return;
    }

    $(this).fr = fr;

    // format allowed types to regular expressions
    if (typeof(allowed_types) == 'string') {
        allowed_types = [allowed_types];
    }
    else if (allowed_types instanceof Array) {
        allowed_types = allowed_types.slice(0);
    }

    // prevent default behaviours
    var preventDefaults = function(e) {
        e.stopPropagation();
        e.preventDefault();
    };

    // selects one allowed file and processes it
    var processFiles = function(files) {
        // matches one file
        var file_matched = false;
        var file = null;
        for (var i = 0; i < files.length; i++)
        {
            file = files[i];

            if (!allowed_types.length) {
                file_matched = true;
                break;
            }

            for (var j = 0; j < allowed_types.length; j++)
            {
                var pattern = allowed_types[j];

                if (file.type.match(pattern)) {
                    file_matched = true;
                    break;
                }
            }

            if (file_matched) {
                break;
            }
        }
        if (!file_matched) {
            return;
        }

        // calls the onload callback
        fr.addEventListener('load', onload_cb);

        // reads matched file
        fr.file = file;
        fr.readAsDataURL(file);
        onready_cb.call(fr);
    }

    // click
    var accept_string = allowed_types.join(',');
    $(this).click(function(e) {
        $('#jquery_file_fake_selector').attr('accept', accept_string).click();
        $('#jquery_file_fake_selector').one('change', function() {
            processFiles(this.files);
            $(this).val('');
        });
        preventDefaults(e);
    });

    // drag and drop
    if (allowed_types instanceof Array && allowed_types.length) {
        for (var i = 0; i < allowed_types.length; i++)
        {
            allowed_types[i] = new RegExp('^' + RegExp.escape(allowed_types[i]) + '$');
        }
    }
    else {
        allowed_types = [/.*/];
    }

    $(this).get(0).addEventListener('dragenter', $(this).setHover, false);
    $(this).get(0).addEventListener('dragleave', $(this).unsetHover, false);
    $(this).get(0).addEventListener('dragover', preventDefaults, false);
    $(this).get(0).addEventListener('drop', function (e) {
        preventDefaults(e);
        $(this).unsetHover();

        if (e.dataTransfer.files.length < 1) {
            return;
        }

        processFiles(e.dataTransfer.files);
        element.trigger('focusout');
    }, false);

    return $(this);
};

jQuery.fn.deleteFile = function() {
    delete $(this).get(0).file;

    return $(this);
};

$(function() {
    // file selector
    $('body').append('<input type="file" id="jquery_file_fake_selector" style="visibility:hidden;position:fixed;top:0;left:0;" accept="" multiple="multiple" />');
})