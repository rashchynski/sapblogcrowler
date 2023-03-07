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

		},

		handleCalendarSelect: function(oEvent) {
		   var blogModel = new sap.ui.model.json.JSONModel();
			blogModel.loadData( "/blog/list/" + this.pyday.format( oEvent.getSource().getSelectedDates()[0].getStartDate() ) );
            controller.getOwnerComponent().setModel(blogModel, "blogs");
		}
	});
});
