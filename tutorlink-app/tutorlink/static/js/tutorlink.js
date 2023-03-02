'use strict';

var tutorlink = {

  summernote_init: function() {
    $('.summernote').summernote();
  },

  init: function() {
    console.log('tutorlink.init()...');
    tutorlink.summernote_init();
    console.log('tutorlink.init() done');
  },
}

$(document).ready(function() {tutorlink.init();});
