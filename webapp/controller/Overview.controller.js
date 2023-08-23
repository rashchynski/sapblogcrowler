sap.ui.define(['sap/ui/core/mvc/Controller', 'sap/ui/unified/DateRange', 'sap/ui/core/format/DateFormat', 'sap/ui/core/library'],
	function(Controller, DateRange, DateFormat, coreLibrary) {
	"use strict";

	var CalendarType = coreLibrary.CalendarType;

    var controller;

	return Controller.extend("com.makra.sdnblog.controller.Overview", {
		oFormatYyyymmdd: null,

		onInit: function() {
		    controller = this;
			this.oFormatYyyymmdd = DateFormat.getInstance({pattern: "MMMM%25yyyy", calendarType: CalendarType.Gregorian});

			this.datasapday = DateFormat.getInstance({pattern: "yyyyMMdd", calendarType: CalendarType.Gregorian});
			this.pyday = DateFormat.getInstance({pattern: "MMMM d, yyyy", calendarType: CalendarType.Gregorian});

			var oStateModel = new sap.ui.model.json.JSONModel();
			controller.dataLoaded = oStateModel.loadData( "/blog/created/count/" + this.oFormatYyyymmdd.format(new Date()) );

			var blogModel = new sap.ui.model.json.JSONModel();
			blogModel.loadData( "/blog/list/" + this.pyday.format(new Date()) ).then(function() {
			} );

            controller.getOwnerComponent().setModel(blogModel, "blogs");

            var calendar = this.byId("calendar");
            controller.dataLoaded.then( function() {

                calendar.addDelegate( {
                    onAfterRendering : function() {

                        var data = oStateModel.getData();
                            $(".sapUiCalItem").each(function(index, item) {
                                var day = controller.datasapday.parse( $(item).attr("data-sap-day") );

                                if(!day)
                                    return;

                                var pyDay = controller.pyday.format(day);

                                var found = data.find( function(row) {
                                    return row[1] === pyDay;
                                } );

                                if( found ) {
                                    $(item).children(".sapUiCalItemText").each(function(ii, iitem) {
                                        $(iitem).append( "<span style='padding-left: 3px;font-size: xx-small;'>" + found[0] + "</span>" );
                                    });
                                }


                            } );

                    }
                } );

                calendar.rerender();


            });

 			this.getRouter()
 				.getRoute("bytag")
 				.attachPatternMatched(function(oEvent) {
 				    var navParam = oEvent.getParameter("arguments");

                    blogModel.setSizeLimit(10000);

    	    		blogModel.loadData( "/blog/list/tag/" +  navParam.tag);
                    controller.getOwnerComponent().setModel(blogModel, "blogs");

 				}, this);

 			this.getRouter()
 				.getRoute("home")
 				.attachPatternMatched(function(oEvent) {
                    var blogModel = new sap.ui.model.json.JSONModel();
                    blogModel.setSizeLimit(10000);
                    blogModel.loadData( "/tags").then(function() {
                    } );

                    controller.getOwnerComponent().setModel(blogModel, "tags");
 				}, this);
		},

        onTagSelected : function(oEvent) {
            this.getRouter().navTo("bytag", {
                tag: oEvent.getParameter("selectedItem").getKey()
            });
        },

		handleCalendarSelect: function(oEvent) {
		   var blogModel = new sap.ui.model.json.JSONModel();
			blogModel.loadData( "/blog/list/" + this.pyday.format( oEvent.getSource().getSelectedDates()[0].getStartDate() ) ).then( function() {

			    var aPromises = [];

                blogModel.getData().forEach( function(item) {
                    aPromises.push(new Promise( function(resolve) {
                        $.ajax( {
                            url : "/blog/tags/" + item.id,
                            success : function(oData) {
                                item.Tags = oData;

                                resolve();
                            }
                        } );

                    } ) );
                } );

                Promise.all(aPromises).then(function() {
                    blogModel.checkUpdate( true );
                } );
            } );

            controller.getOwnerComponent().setModel(blogModel, "blogs");
		},

        onOpenFavourites: function(oEvent) {
            this.getRouter().navTo("bylist", {
                list : 1,
                ts   : Date.now()
            });
        },

        onOpenRead: function(oEvent) {
            this.getRouter().navTo("bylist", {
                list : 2,
                ts   : Date.now()
            });
        },

        getRouter: function() {
            return this.getOwnerComponent().getRouter();
        }
	});
});
