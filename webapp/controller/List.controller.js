sap.ui.define(['sap/ui/core/mvc/Controller', 'sap/ui/unified/DateRange', 'sap/ui/core/format/DateFormat', 'sap/ui/core/library'],
    function (Controller, DateRange, DateFormat, coreLibrary) {
        "use strict";

        const CalendarType = coreLibrary.CalendarType;
        const dbFormat = DateFormat.getInstance({pattern: "yyyyMMdd", calendarType: CalendarType.Gregorian});
        const uiFormat = DateFormat.getInstance({pattern: "yyyy/MM/dd", calendarType: CalendarType.Gregorian});


        var controller, me;

        const fnLoadBlogs = function (uri, uriCount) {
            const blogModel = new sap.ui.model.json.JSONModel();
            blogModel.setSizeLimit(10000);
            blogModel.loadData(uri).then(function () {
                var aPromises = [];

                blogModel.getData().forEach(function (item) {
                    item.created = uiFormat.format( dbFormat.parse( item.created ) );

                    if( !item.link.startsWith("https://blogs.sap.com") ) {
                        item.link = `https://blogs.sap.com${item.link}`
                    }
                    aPromises.push(new Promise(function (resolve) {
                        $.ajax({
                            url		: "/blog/tags/" + item.blog_id,
                            success	: function (oData) {
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
        };

        return Controller.extend("com.makra.sdnblog.controller.Overview", {
            onInit: function () {
                controller = this;
                me = this;



                me.ListsModel = controller.getOwnerComponent().getModel("lists");
                me.FavListsModel = controller.getOwnerComponent().getModel("favLists");

                me.uiModel = new sap.ui.model.json.JSONModel({
                    inList: false,
                    inTag: false,
                    list: "",
                    tag: ""
                });

                controller.getOwnerComponent().setModel(me.uiModel, "ui");

                /*
                    /blog/search/
                    /blog/list/date/
                    /blog/list/tag/
                    /list/
                */
                this.getRouter()
                    .getRoute("search")
                    .attachPatternMatched(function (oEvent) {
                        const navParam = oEvent.getParameter("arguments");
                        fnLoadBlogs("/blog/search/" + encodeURIComponent("%" + navParam.search + "%"));

                        me.uiModel.setProperty("/inTag", false);
                        me.uiModel.setProperty("/inList", false);

                        me.byId("BlogList").setGrowing(true);
                    }, this);

                this.getRouter()
                    .getRoute("bydate")
                    .attachPatternMatched(function (oEvent) {
                        const navParam = oEvent.getParameter("arguments");
                        fnLoadBlogs("/blog/list/date/" + navParam.date);

                        me.uiModel.setProperty("/inTag", false);
                        me.uiModel.setProperty("/inList", false);

                        me.byId("BlogList").setGrowing(false);

                    }, this);

                this.getRouter()
                    .getRoute("byauthor")
                    .attachPatternMatched(function (oEvent) {
                        const navParam = oEvent.getParameter("arguments");
                        fnLoadBlogs("/blog/author/" + navParam.author);

                        me.uiModel.setProperty("/inTag", false);
                        me.uiModel.setProperty("/inList", false);

                        me.byId("BlogList").setGrowing(false);

                    }, this);

                this.getRouter()
                    .getRoute("bytag")
                    .attachPatternMatched(function (oEvent) {
                        const navParam = oEvent.getParameter("arguments");
                        fnLoadBlogs("/blog/list/tag/" + navParam.tag);

                        $.ajax({
                            url: "/tag/" + navParam.tag,
                            success: function (oData) {
                                me.uiModel.setProperty("/tag", oData[0]);
                            }
                        });

                        me.uiModel.setProperty("/inList", false);
                        me.uiModel.setProperty("/inTag", true);
                        me.uiModel.setProperty("/list", navParam.tag);

                        me.byId("BlogList").setGrowing(true);
                    }, this);

                this.getRouter()
                    .getRoute("bylist")
                    .attachPatternMatched(function (oEvent) {
                        var navParam = oEvent.getParameter("arguments");
                        fnLoadBlogs("/list/" + navParam.list);

                        me.uiModel.setProperty("/inTag", false);
                        me.uiModel.setProperty("/inList", true);
                        me.uiModel.setProperty("/list", navParam.list);

                        me.byId("BlogList").setGrowing(false);
                    }, this);
            },

            doLoadMoreData: function (oEvent) {

            },

            onRemoveFromList: function (oEvent) {
                var list = controller.getOwnerComponent().getModel("ui").getProperty("/list");
                var bindingCtx = oEvent.getSource().getBindingContext("blogs");
                var blogModel = new sap.ui.model.json.JSONModel();

                blogModel.loadData("/list/remove/" + list + "/" + bindingCtx.getObject().blog_id).then(function () {
                    controller.getRouter().navTo("bylist", {
                        list: list,
                        ts: Date.now()
                    }, {}, true);
                });
            },

            getRouter: function () {
                return this.getOwnerComponent().getRouter();
            },

            onToggleTagFavourites: async function (oEvent) {
                if( me.uiModel.getProperty("/tag/isFavourite")  === 1 ) {
                    await fetch( "/tag/list/favourite/remove/" + me.uiModel.getProperty("/tag/id") );
                    me.uiModel.setProperty("/tag/isFavourite", 0);
                } else {
                    await fetch("/tag/list/favourite/" + me.uiModel.getProperty("/tag/id"));
                    me.uiModel.setProperty("/tag/isFavourite", 1);
                }
            },

            onToggleFavourites: function (oEvent) {
                me.onToggleList(oEvent, "1");
            },

            onToggleReading: function (oEvent) {
                me.onToggleList(oEvent, "2");
            },

            onToggleList: function (oEvent, listId) {
                var bindingCtx = oEvent.getSource().getBindingContext("blogs");

                let blogId = bindingCtx.getObject().blog_id,
                    listMap = me.ListsModel.getProperty(`/map/${listId}`) || {},
                    action = "";

                if(listMap[blogId]) {
                    delete listMap[blogId];
                    action = "remove";
                } else {
                    listMap[blogId] = { blog_id : blogId };
                    action = "add";
                }

                me.ListsModel.setProperty(`/map/${listId}`, listMap);
                controller.getOwnerComponent().getModel("blogs").checkUpdate(true);

                fetch(`/list/${action}/${listId}/${blogId}`);
            },


            onNavByTag: function (oEvent) {
                this.getRouter().navTo("bytag", {
                    tag: oEvent.getSource().getBindingContext("blogs").getObject().tag_id
                });
            },

            onNavByAuthor: function (oEvent) {
                this.getRouter().navTo("byauthor", {
                    tag: oEvent.getSource().getBindingContext("blogs").getObject().author
                });
            },

            onMarkAsRead: function (oEvent) {
                var bindingCtx = oEvent.getSource().getBindingContext("blogs");
                var oStateModel = new sap.ui.model.json.JSONModel();
                oStateModel.loadData("/list/add/3/" + bindingCtx.getObject().blog_id);
            },

            isRead: function (blogId) {
                return !!me.ListsModel.getProperty("/map/3/" + blogId);
            },

            isInFavsColor: function (blogId) {
                return me.isInFavs(blogId) ? "rgb(57, 136, 193)" : "rgba(57, 136, 193, 0.3)" ;
            },

            isInFavs: function (blogId) {
                return !!me.ListsModel.getProperty("/map/1/" + blogId);
            },

            isInReadColor: function (blogId) {
                return me.isInRead(blogId) ? "rgb(57, 136, 193)" : "rgba(57, 136, 193, 0.3)" ;
            },

            isInRead: function (blogId) {
                return !!me.ListsModel.getProperty("/map/2/" + blogId);
            },

            isTagFavourite(tag_id) {
                const modelData = me.FavListsModel.getProperty(`/map/${tag_id}/isFavourite`);

                return !!modelData;
            }
        });
    });
