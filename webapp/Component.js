sap.ui.define([
	"sap/ui/core/UIComponent",
], function (UIComponent, Device, models, IconPool, JSONModel, RegistrationUtils, DatePicker, DateFormat) {
	"use strict";

	var component;

	return UIComponent.extend("com.makra.sdnblog.Component", {

		metadata: {
			manifest: "json"
		},

		init: function () {
		    component = this;

			UIComponent.prototype.init.apply(component, arguments);

			component.getRouter().initialize();
		}
	});
});