sap.ui.define(['sap/ui/core/mvc/Controller', 'sap/ui/unified/DateRange', 'sap/ui/core/format/DateFormat', 'sap/ui/core/library'],
	function(Controller, DateRange, DateFormat, coreLibrary) {
	"use strict";

	var CalendarType = coreLibrary.CalendarType;

    var controller, me;

	return Controller.extend("com.makra.sdnblog.controller.Overview", {
		onInit: function() {
		    controller = this;
			me = this;

			me.ListsModel = controller.getOwnerComponent().getModel("lists");

			me.uiModel = new sap.ui.model.json.JSONModel( {
				inList : false,
				inTag  : false,
				list   : "",
				tag    : ""
			} );

			controller.getOwnerComponent().setModel(me.uiModel, "ui");

			const fnLoadBlogs = function(uri) {
				const blogModel = new sap.ui.model.json.JSONModel();
				blogModel.setSizeLimit(10000);
				blogModel.loadData( uri ).then( function() {
					var aPromises = [];

					blogModel.getData().forEach(function (item) {
						aPromises.push(new Promise(function (resolve) {
							$.ajax({
								url: "/blog/tags/" + item.blog_id,
								success: function (oData) {
									item.Tags = oData;

									resolve();
								}
							});

						}));
					});

					Promise.all(aPromises).then(function () {
						blogModel.checkUpdate(true);
					});
				});

				controller.getOwnerComponent().setModel(blogModel, "blogs");
			} ;

			this.getRouter()
				.getRoute("bydate")
				.attachPatternMatched(function(oEvent) {
					const navParam = oEvent.getParameter("arguments");
					fnLoadBlogs("/blog/list/date/" +  navParam.date);

					me.uiModel.setProperty("/inTag", false );
					me.uiModel.setProperty("/inList", false);

				}, this);

			this.getRouter()
				.getRoute("bytag")
				.attachPatternMatched(function(oEvent) {
					const navParam = oEvent.getParameter("arguments");
					fnLoadBlogs( "/blog/list/tag/" +  navParam.tag ) ;

					$.ajax({
						url: "/tag/" + navParam.tag,
						success: function (oData) {
							me.uiModel.setProperty("/tag", oData[0]);
						}
					});

					me.uiModel.setProperty("/inList", false);
					me.uiModel.setProperty("/inTag", true );
					me.uiModel.setProperty("/list", navParam.tag );
				}, this);

			this.getRouter()
				.getRoute("bylist")
				.attachPatternMatched(function(oEvent) {
					var navParam = oEvent.getParameter("arguments");
					fnLoadBlogs( "/list/" +  navParam.list ) ;

					me.uiModel.setProperty("/inTag", false );
					me.uiModel.setProperty("/inList", true);
					me.uiModel.setProperty("/list", navParam.list);
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

		onToggleTagFavourites : function(oEvent) {
			$.ajax({
				url: "/tag/list/favourite/" + me.uiModel.getProperty("/tag/id")
			});
		},

		onToggleFavourites : function(oEvent) {
			var bindingCtx = oEvent.getSource().getBindingContext("blogs");
			var oStateModel = new sap.ui.model.json.JSONModel();
			oStateModel.loadData( "/list/add/1/" + bindingCtx.getObject().blog_id );
		},

		onToggleReading : function(oEvent) {
			var bindingCtx = oEvent.getSource().getBindingContext("blogs");
			var oStateModel = new sap.ui.model.json.JSONModel();
			oStateModel.loadData( "/list/add/2/" + bindingCtx.getObject().blog_id );
		},

		onNavByTag : function(oEvent) {
			this.getRouter().navTo("bytag", {
				tag: oEvent.getSource().getBindingContext("blogs").getObject().tag_id
			});
		},

		onMarkAsRead  :function(oEvent) {
			var bindingCtx = oEvent.getSource().getBindingContext("blogs");
			var oStateModel = new sap.ui.model.json.JSONModel();
			oStateModel.loadData( "/list/add/3/" + bindingCtx.getObject().blog_id );
		},

		isRead : function(blogId) {
			return !!me.ListsModel.getProperty("/map/3/" + blogId);
		},

		isInFavs : function(blogId) {
			return !!me.ListsModel.getProperty("/map/1/" + blogId);
		},

		isInRead : function(blogId) {
			return !!me.ListsModel.getProperty("/map/2/" + blogId);
		}

	});
});
