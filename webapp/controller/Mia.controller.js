sap.ui.define(['sap/ui/core/mvc/Controller', 'sap/ui/unified/DateRange', 'sap/ui/core/format/DateFormat', 'sap/ui/core/library'],
    function (Controller, DateRange, DateFormat, coreLibrary) {
        "use strict";

        const PAGE_SIZE = 20;

        var controller, me;


        return Controller.extend("com.makra.sdnblog.controller.Mia", {
            onInit: function () {
                controller = this;
                me = this;

                me.generateNext();
            },

            generateNext : function() {
                let a = Math.floor(Math.random() * (9 - 1 + 1)) + 1,
                    b = Math.floor(Math.random() * (9 - 1 + 1)) + 1;

                me.answer = a*b;

                this.byId( "Question" ).setText( `${a} * ${b} = `);
            },

            onAnswer : function(oEvent) {
                if( parseInt( oEvent.getParameter("value") ) === me.answer ) {
                    oEvent.getSource().setValue("");
                    sap.m.MessageToast.show("Правильно!", { at : "CenterTop"} );

                    me.generateNext();
                } else {
                    sap.m.MessageToast.show("Не Правильно!", { at : "CenterTop"} );
                }
            }
        });
    });
