var DEBUG = true;

// logging
(function() {

    var levels = ['debug', 'info', 'warn', 'error', 'critical', 'log'];

    if (!window.console || !DEBUG) {
        // no console, so no logging
        // assign empty function to avoid errors
        window.console = {
            log: function () {}
        };
    }

    for (ii = 0; ii < levels.length; ii++) {
        if (!console[levels[ii]]) {
            console[levels[ii]] = console.log;
        }
    }

})();

(function($) {

    function Beergame (opts) {
    }

    Beergame.prototype.init = function() {
        var locPath = location.pathname.split('/'), params, that = this;
        this.gameSlug = locPath[2];
        this.role = locPath[3];
        this.period = null;

        this.BUTTONS = ['next-period-btn', 'step1-btn', 'step2-btn', 'ship-btn', 'order-btn'];
        this.currentBtn = 0; // index of BUTTONS

        this.initUI();

        $('.button').live('click', $.proxy(this.initButtonHandlers, this));

        $('#add-game-btn').live('click', this.createGame);

        params = $.param({game_slug: this.gameSlug, role: this.role});
        this.doAjax('/api/periods/json/?' + params, 'GET', '', '', function(data, textStatus, xhr) {
                data = data[0];
                that.period = data;
        });
    };

    Beergame.prototype._getCurBtnId = function() {
        return this.BUTTONS[this.currentBtn];
    };

    Beergame.prototype.initButtonHandlers = function(evt) {
        console.log('button clicked...');
        var elm = evt.target;
        $(elm).attr('disabled', true);
        switch (elm.id) {
            case 'next-period-btn':
                console.log('clicked next period');
                this.currentBtn = $.inArray(elm.id, this.BUTTONS);
                this.nextPeriod();
            break;
            case 'step1-btn':
            break;
        }
    };

    Beergame.prototype.initUI = function() {
        $('.button').attr('disabled', true);
        $('#next-period-btn').attr('disabled', false);
    };

    Beergame.prototype.defaultAjaxError = function(xhr, textStatus, error) {

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
        var loading = $('#loading');
        if (method === 'POST' && data === '') {
            data = JSON.stringify({});
        }

        if (dataType === '') {
            dataType = 'json';
        }

        loading.removeClass('hidden');

        $.ajax({
            cache: false,
            complete: function(xhr, settings) {
                loading.addClass('hidden');
            },
            contentType: 'application/json',
            data: data,
            dataType: dataType,
            error: [this.defaultAjaxError, eCallback],
            success: sCallback,
            timeout: 3000,
            type: method,
            url: url
        });

    };

    Beergame.prototype.defaultBtnAjaxError = function(xhr, textStatus, error) {
        console.log('in defaultBtnAjaxError');
        $('#'+this._getCurBtnId()).attr('disabled', false);
    };

    Beergame.prototype.doBtnAjax = function(url, method, data, dataType, sCallback) {
        console.log('in doBtnAjax');

        function sCallback(data, textStatus, xhr) {
            $('#'+this._getCurBtnId()).attr('disabled', false);
        }
        this.doAjax(url, method, data, dataType, $.proxy(sCallback, this), $.proxy(this.defaultBtnAjaxError, this));
    };

    /* Adds game to the UI */
    Beergame.prototype._addGame = function() {
        this.doAjax('/g/html/?template=game_listing', 'GET', '', 'text', function(data, textStatus, xhr) {
           $('#game-listing-wrapper').html(data);
        });
    };

    Beergame.prototype.createGame = function() {
        var that = this, groupName = $('#id_group_name').val(),
            numPeriods = $('#id_num_periods').val(),
            data = JSON.stringify({
                        group_name: groupName,
                        num_periods: numPeriods
                    });

        this.doAjax('/api/games/json/', 'POST', data, 'text', function(data, textStatus, xhr) {
            that._addGame();
        });
    };

    Beergame.prototype.nextPeriod = function() {
        // create next period object
        var that = this, params = $.param({game_slug: this.gameSlug, role: this.role});
        this.doBtnAjax('/api/periods/json/?' + params, 'POST', '', 'text', function(data, textStatus, xhr) {
            console.log(textStatus);
            that.incrPeriod();
        });
    };

    Beergame.prototype.incrPeriod = function() {
        var per = $('#period');

        curPer = parseInt(per.text());

        if (isNaN(curPer)) {
            per.text(1);
        } else {
            per.text(curPer+1);
        }
    };

    window.Beergame = Beergame;
}(jQuery));

(function($) {
    $(function() {
        var bg = new Beergame();
        bg.init();
    });
}(jQuery));
