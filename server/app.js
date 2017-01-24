Vue.component('event-item', {
    template: '\
    <a href="#" class="list-group-item">\
        <h4 class="list-group-item-heading">\
            <i class="glyphicon glyphicon-bullhorn"></i>\
            {{ eve.name }}\
        </h4>\
        <h5>\
            <i class="glyphicon glyphicon-calendar" v-if="eve.date"></i>\
            {{ eve.date }}\
        </h5>\
        <p class="list-group-item-text" v-if="eve.desc">{{ eve.desc }}</p>\
    </a>\
    ',
    props: ['eve']
});

Vue.component('xuequ-item', {
    template: '\
    <a href="#" class="list-group-item">\
        <h4 class="list-group-item-heading">\
            <i class="glyphicon glyphicon-bullhorn"></i>\
            {{ xq }}\
        </h4>\
        <button class="btn btn-primary btn-sm" v-on:click="$emit(\'qxq\')">Query</button>\
    </a>\
    ',
    props: ['xq']
});

new Vue({
    el: '#events',    // target the container div with id "events"
    data: {    // view model
        regionb: [],
        regionb_selected: '',
        xuequ: [],
        xiaoqu: []
    },
    mounted: function() {    // will run when app loads
        // when app loads, we want to call it to init some data from wherever place
        this.initRegionb();
    },
    methods: {    // register custom methods for app
        initRegionb: function() {
            this.$http.get('http://192.168.33.11/regionb').then(function(response) {
                var regionb = JSON.parse(response.body)['regionb']
                for (r in regionb) {
                    this.regionb.push({ text: regionb[r], value: regionb[r] });
                }
            }, function(error) {
                console.log(error);
            });
        },

        queryRegionb: function() {
            this.$http.get('http://192.168.33.11/xuequ', {params: {regionb: this.regionb_selected}}).then(function(response) {
                this.xuequ = [];
                var xuequ = JSON.parse(response.body)['xuequ'];
                for (i in xuequ) {
                    this.xuequ.push(xuequ[i]);
                }
            }, function(error) {
                console.log(error)
            });
        },

        queryXuequ: function(xq) {
            this.$http.get('http://192.168.33.11/xiaoqu', {params: {xuequ: xq}}).then(function(response) {
                this.xiaoqu = [];
                var xiaoqu = JSON.parse(response.body)['xiaoqu'];
                for (i in xiaoqu) {
                    this.xiaoqu.push(xiaoqu[i]);
                }
            }, function(error) {
                console.log(error)
            });
        },

        queryXiaoqu: function(xq) {
            this.$http.get('http://192.168.33.11/ershou', {params: {xiaoqu: xq}}).then(function(response) {
                this.ershou = [];
                var ershou = JSON.parse(response.body)['ershou'];
                for (i in ershou) {
                    this.ershou.push(ershou[i]);
                }
            }, function(error) {
                console.log(error)
            });
        }
    }
});
