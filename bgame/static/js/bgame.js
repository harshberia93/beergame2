(function($) {

    function Beergame (opts) {
    }

    Beergame.prototype.init = function() {
        var locPath = location.pathname.split('/'), params, that = this;
        this.gameSlug = locPath[2];
        this.role = locPath[3];
        this.period = null;

        $('#next_period_btn').live('click', function() {
            console.log('triggered event');
            that.nextPeriod();
            $(this).button('option', 'disabled', true);
        });

        $('#add-game-btn').live('click', function() {
            that.createGame();
        });
        
        params = $.param({game_slug: this.gameSlug, role: this.role});
        this.doAjax('/api/periods/json/?' + params, 'GET', '', '', function(data, textStatus, xhr) {
                data = data[0];
                that.period = data; 
        });
    };

    /*
     * url
     * method: HTTP -- GET, POST, PUT, or DELETE
     * data: data to send to the server
     * dataType: excepted datatype from the server
     * sCallback: success callback
     * eCallback: error callback
     */
    Beergame.prototype.doAjax = function(url, method, data, dataType, sCallback, eCallback) {
        if (method === 'POST' && data === '') {
            data = JSON.stringify({}); 
        }

        if (dataType === '') {
            dataType = 'json';
        }

        $.ajax({
            cache: false,
            contentType: 'application/json',
            data: data,
            dataType: dataType,
            error: function(xhr, textStatus, error) {

                if (textStatus === 'timeout') {
                    $.jGrowl('ERROR: Could not connect to server.  Please check your internet connection and try again.');
                } else if (error === 'BAD REQUEST') {
                    $.jGrowl('ERROR: ' + xhr.responseText, {position: 'bottom-right'}); 
                }
                
                console.log('####error has occurred####');
                console.log('error:' + error);
                console.log('textStatus:' + textStatus);
                console.log('xhr.status:' + xhr.status);
                console.log('xhr.statusText:' + xhr.statusText);
                console.log('xhr.getAllResponseHeaders:' + xhr.getAllResponseHeaders);
            },
            success: sCallback,
            timeout: 3000,
            type: method,
            url: url
        });

    };

    /* Adds game to the UI */
    Beergame.prototype._addGame = function() {
        console.log('called _addGame');
        this.doAjax('/g/html/?template=game_listing', 'GET', '', 'text', function(data, textStatus, xhr) {
           $('#game-listing-wrapper').html(data); 
        });
    };

    Beergame.prototype.createGame = function() {
        console.log('in createGame');
        var that = this, groupName = $('#id_group_name').val(),
            numPeriods = $('#id_num_periods').val(),
            data = JSON.stringify({ 
                        group_name: groupName, 
                        num_periods: numPeriods 
                    });

        this.doAjax('/api/games/json/', 'POST', data, 'text', function(data, textStatus, xhr) {
            console.log('in callback');
            that._addGame(); 
        });
    };

    Beergame.prototype.nextPeriod = function() {
        // create next period object 
        var params = $.param({game_slug: this.gameSlug, role: this.role});
        this.doAjax('/api/periods/json/?' + params, 'POST', '', '', function(data, textStatus, xhr) {
            console.log(textStatus); 
        });
    };

    window.Beergame = Beergame;
}(jQuery));

(function($) {
    $(function() {
        var bg = new Beergame();    
        bg.init();
    }); 
}(jQuery));
