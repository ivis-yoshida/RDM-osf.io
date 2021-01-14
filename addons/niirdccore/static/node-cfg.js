'use strict';

var $ = require('jquery');
var m = require('mithril');
var ko = require('knockout');
var Raven = require('raven-js');
var osfHelpers = require('js/osfHelpers');
var ChangeMessageMixin = require('js/changeMessage');
var SaveManager = require('js/saveManager');

var SHORT_NAME = 'niirdccore';
var logPrefix = `[${SHORT_NAME}] `;


function NodeSettings() {
  var self = this;
  self.baseUrl = window.contextVars.node.urls.api + SHORT_NAME + '/';

  ChangeMessageMixin.call(self);

  self.loadConfig = function () {
    var url = self.baseUrl + 'settings';
    console.log(logPrefix, 'loading: ', url);
  }
}
var settings = new NodeSettings();
osfHelpers.applyBindings(settings, `#${SHORT_NAME}Scope`);
settings.loadConfig();