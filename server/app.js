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

new Vue({
    el: '#events',    // target the container div with id "events"
    data: {    // view model
        eve: {name: '', desc: '', date: ''},
        events: []
    },
    mounted: function() {    // will run when app loads
        // when app loads, we want to call it to init some data from wherever place
        this.fetchEvents();
    },
    methods: {    // register custom methods for app
        fetchEvents: function() {
            var events = [
                { id: 1, name: 'Initialized', desc: 'init process done', date: '2016-12-12' },
                { id: 2, name: 'Data Loaded', desc: 'data loading process done', date: '2016-12-13' },
                { id: 3, name: 'Analysis Done', desc: 'analysis process done', date: '2016-12-14' }
            ];
            for (var i in events) {
                this.events.push(events[i]);
            }
        },

        addEvent: function() {
            if (this.eve.name) {
                this.events.push(this.eve);
                this.eve =  {name: '', desc: '', date: ''};
            }
        }
    }
});
