(function($) {
    function Beergame (opts) {
        this.ajaxBaseUrl = '/api';

        console.log('created beergame obj');
    };
    Beergame.prototype.init = function() {
        var locPath = location.pathname.split('/'), params, that = this;
        this.gameSlug = locPath[2];
        this.role = locPath[3];
        this.period = null;

        $(this).bind('inited', this.test);
        
        
        params = $.param({game_slug: this.gameSlug, role: this.role});
        this.doAjax('/periods/?' + params, 'GET', function(data, textStatus, xhr) {
                data = data[0];
                that.period = data; 
                $(that).trigger('inited');
        });
    };
    Beergame.prototype.nextPeriod = function() {
        // create next period object 
        this.doAjax('/periods/', 'POST');
    };
    Beergame.prototype.doAjax = function(url, method, data, callback) {
        url = this.ajaxBaseUrl + url;
        var that = this;
        $.ajax({
            cache: false,
            contentType: 'json',
            data: data,
            dataType: 'json',
            success: callback,
            type: method,
            url: url,
        });

    };
    Beergame.prototype.test = function() {
        console.log(this.gameSlug);
        console.log(this.role);
        console.log(this.period);
    };

    window.Beergame = Beergame;
}(jQuery));

(function($) {
    $(function() {
        var bg = new Beergame();    
        bg.init();
    }); 
}(jQuery));
