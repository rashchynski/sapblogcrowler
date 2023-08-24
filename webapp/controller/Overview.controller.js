sap.ui.define(['sap/ui/core/mvc/Controller', 'sap/ui/unified/DateRange', 'sap/ui/core/format/DateFormat', 'sap/ui/core/library'],
	function(Controller, DateRange, DateFormat, coreLibrary) {
	"use strict";

	var CalendarType = coreLibrary.CalendarType;

    var controller;

	return Controller.extend("com.makra.sdnblog.controller.Overview", {
		oFormatYyyymmdd: null,

		onInit: function() {
		    controller = this;

			this.datasapday = DateFormat.getInstance({pattern: "yyyyMMdd", calendarType: CalendarType.Gregorian});
            this.countByDate = DateFormat.getInstance({pattern: "yyyyMM%25", calendarType: CalendarType.Gregorian});

            const oStateModel = new sap.ui.model.json.JSONModel();
            controller.dataLoaded = oStateModel.loadData( "/blog/created/count/" + this.countByDate.format(new Date()) );

            const oListsModel = new sap.ui.model.json.JSONModel();
            oListsModel.loadData( "/list" ).then( function() {
                const aList = oListsModel.getData(),
                listMap = {};

                aList.forEach( function(listItem) {
                    const list = listMap[listItem.list_id] || {};
                    list[listItem.blog_id] = listItem;
                    listMap[listItem.list_id] = list;
                } );

                oListsModel.setProperty("/list", aList);
                oListsModel.setProperty("/map", listMap);
            } );
            controller.getOwnerComponent().setModel(oListsModel, "lists");

            const oFavListsModel = new sap.ui.model.json.JSONModel();
            oFavListsModel.loadData( "/tag/list/favourite" ).then( function() {
                const aList = oListsModel.getData(),
                    listMap = {};

                aList.forEach( function(listItem) {
                    const list = listMap[listItem.list_id] || {};
                    list[listItem.blog_id] = listItem;
                    listMap[listItem.list_id] = list;
                } );

                oListsModel.setProperty("/list", aList);
                oListsModel.setProperty("/map", listMap);
            } );
            controller.getOwnerComponent().setModel(oFavListsModel, "favLists");


            controller.dataLoaded.then( function() {
                controller.byId("calendar").addDelegate( {
                    onAfterRendering : function() {
                        var data = oStateModel.getData();
                        $(".sapUiCalItem").each(function(index, item) {
                            var day =  $(item).attr("data-sap-day");

                            if(!day)
                                return;

                            var found = data.find( function(row) {
                                return row[1] === parseInt( day );
                            } );

                            if( found ) {
                                $(item).children(".sapUiCalItemText").each(function(ii, iitem) {
                                    $(iitem).append( "<span style='padding-left: 3px;font-size: xx-small;'>" + found[0] + "</span>" );
                                });
                            }
                        } );
                    }
                } );

                controller.byId("calendar").rerender();
            });

 			this.getRouter()
 				.getRoute("home")
 				.attachPatternMatched(function(oEvent) {
                    controller.getRouter().navTo("bydate", {
                        date : this.datasapday.format(new Date())
                    });
				}, this);
		},

        onNavByTag : function(oEvent) {
            this.getRouter().navTo("bytag", {
                tag: oEvent.getSource().getContextBinding("favLists").getObject().id
            });
        },

		handleCalendarSelect: function(oEvent) {
            controller.getRouter().navTo("bydate", {
                date : this.datasapday.format( oEvent.getSource().getSelectedDates()[0].getStartDate()  )
            });
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
