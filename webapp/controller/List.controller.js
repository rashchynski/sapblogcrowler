sap.ui.define(['sap/ui/core/mvc/Controller', 'sap/ui/unified/DateRange', 'sap/ui/core/format/DateFormat', 'sap/ui/core/library'],
	function(Controller, DateRange, DateFormat, coreLibrary) {
	"use strict";

	var CalendarType = coreLibrary.CalendarType;

    var controller;

	return Controller.extend("com.makra.sdnblog.controller.Overview", {
		oFormatYyyymmdd: null,

		onInit: function() {
		    controller = this;

			controller.getOwnerComponent().setModel(new sap.ui.model.json.JSONModel( {
				inList : false
			} ), "ui");


			this.getRouter()
				.getRoute("bylist")
				.attachPatternMatched(function(oEvent) {
					var navParam = oEvent.getParameter("arguments");

					var blogModel = new sap.ui.model.json.JSONModel();
					blogModel.setSizeLimit(10000);
					blogModel.loadData( "/list/" +  navParam.list).then( function() {

						blogModel.getData().forEach( function(item) {
							$.ajax( {
								url : "/blog/tags/" + item.blog_id,
								success : function(oData) {
									item.Tags = oData;
								}
							} );
						} );
					} );
					controller.getOwnerComponent().setModel(blogModel, "blogs");

					controller.getOwnerComponent().getModel("ui").setProperty("/inList", true);
					controller.getOwnerComponent().getModel("ui").setProperty("/list", navParam.list);
				}, this);
        },


		onRemoveFromList : function(oEvent) {
			var list = controller.getOwnerComponent().getModel("ui").getProperty("/list" );
			var bindingCtx = oEvent.getSource().getBindingContext("blogs");
			var blogModel = new sap.ui.model.json.JSONModel();

			blogModel.loadData( "/list/remove/" + list + "/" + bindingCtx.getObject().blog_id ).then(function() {
				controller.getRouter().navTo("bylist", {
					list : list,
					ts   : Date.now()
				}, {}, true);
			} );
		},

		getRouter: function() {
            return this.getOwnerComponent().getRouter();
        },

		onToggleFavourites : function(oEvent) {
			var bindingCtx = oEvent.getSource().getBindingContext("blogs");
			var oStateModel = new sap.ui.model.json.JSONModel();
			oStateModel.loadData( "/list/add/1/" + bindingCtx.getObject().id );
		},

		onToggleReading : function(oEvent) {
			var bindingCtx = oEvent.getSource().getBindingContext("blogs");
			var oStateModel = new sap.ui.model.json.JSONModel();
			oStateModel.loadData( "/list/add/2/" + bindingCtx.getObject().id );
		}

	});
});
