sap.ui.define(['sap/ui/core/mvc/Controller', 'sap/ui/unified/DateRange', 'sap/ui/core/format/DateFormat', 'sap/ui/core/library'],
	function(Controller, DateRange, DateFormat, coreLibrary) {
	"use strict";

	var CalendarType = coreLibrary.CalendarType;

    var controller,me;

    const chartFormat = DateFormat.getInstance({pattern: "yyyy-MM-dd", calendarType: CalendarType.Gregorian});
    const titleFormat = DateFormat.getInstance({pattern: "MMMM yyyy", calendarType: CalendarType.Gregorian});

	return Controller.extend("com.makra.sdnblog.controller.Overview", {
		onInit: function() {
		    controller = me = this;

            this.datasapday = DateFormat.getInstance({pattern: "yyyyMMdd", calendarType: CalendarType.Gregorian});
            this.countByDate = DateFormat.getInstance({pattern: "yyyyMM%25", calendarType: CalendarType.Gregorian});

            let navModelObject = {
                CurrentMonth : new Date()
            };

            Object.defineProperty(navModelObject, "CurrentMonthTitle", {
                get : function() {
                    return titleFormat.format(this.CurrentMonth);
                }
            });

            me.mainModel = new sap.ui.model.json.JSONModel( navModelObject );

            me.getView().setModel( me.mainModel );

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
                const aList = oFavListsModel.getData(),
                    listMap = {};

                aList.forEach( function(listItem) {
                    listMap[listItem.id] = listItem;
                } );

                oFavListsModel.setProperty("/map", listMap);
            } );
            controller.getOwnerComponent().setModel(oFavListsModel, "favLists");

            me.cal = new CalHeatmap();

            me.cal.on('click', (event, timestamp, value) => {
                controller.getRouter().navTo("bydate", {
                    date : this.datasapday.format( new Date(timestamp + new Date().getTimezoneOffset()*60*1000 )  )
                });
            });

            controller.loadMonth(new Date());

 			this.getRouter()
 				.getRoute("home")
 				.attachPatternMatched(function(oEvent) {
                    controller.getRouter().navTo("bydate", {
                        date : this.datasapday.format(new Date())
                    });
				}, this);
		},

        navNext: function() {
            let currentMonth = me.mainModel.getProperty("/CurrentMonth");
            currentMonth.setMonth(currentMonth.getMonth() + 1);
            currentMonth.setDate(1);
            me.mainModel.setProperty("/CurrentMonth", currentMonth);

            controller.loadMonth();

            controller.getRouter().navTo("bydate", {
                date : this.datasapday.format( currentMonth )
            });

        },

        navPrev : function() {
            let currentMonth = me.mainModel.getProperty("/CurrentMonth");
            currentMonth.setDate(1);
            currentMonth.setMonth(currentMonth.getMonth() - 1);
            me.mainModel.setProperty("/CurrentMonth", currentMonth);

            controller.loadMonth();

            controller.getRouter().navTo("bydate", {
                date : this.datasapday.format( currentMonth )
            });
        },

        loadMonth : async function () {
            let date  = me.getView().getModel().getProperty("/CurrentMonth"),
            response  = await fetch( "/blog/created/count/" + this.countByDate.format( date ) ),
                data  = await response.json(),
            chartData = data.map( item => {
                return {
                    date : chartFormat.format(controller.datasapday.parse( item[1] ) ),
                    value :  item[0]
                }
            } );

            me.cal.paint(
                {
                    data: {
                        source: chartData,
                        x : 'date',
                        y : d => +d['value'],
                        defaultValue : 0
                    },
                    date: { start: date },
                    range: 1,
                    scale: {
                        color: {
                            type: 'linear',
                            scheme: 'Blues',
                            domain: [0, 50]
                        }
                    },
                    domain: {
                        type: 'month',
                        padding: [10, 10, 10, 10],
                        label: {offset : { x : -1000 }, position: 'top'},
                    },
                    subDomain: {type: 'xDay', radius: 2, width: 35, height: 35, label: 'D'}
                },
                [
                    [
                        Tooltip,
                        {
                            text: function (date, value, dayjsDate) {
                                return value;
                            },
                        },
                    ],
                ]
            );


        },

        onSearch : function(oEvent) {
            this.getRouter().navTo("search", {
                search : oEvent.getParameter("value")
            });
        },

        onNavByTag : function(oEvent) {
            this.getRouter().navTo("bytag", {
                tag: oEvent.getSource().getBindingContext("favLists").getObject().id
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
        },

        onPurgeList: function(oEvent) {
            fetch("/list/purge/2");
        },

        __ : function()
        {
           fetch("/blog/created/count/" + me.countByDate.format( new Date() ) ).then();
        }
	});
});
