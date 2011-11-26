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

    // GameUI interacts with the user interface of the game.
    function GameUI(opts) {
        this.opts = opts;
    }

   /**
    * Get the current period as an integer.
    */
    GameUI.prototype.getPeriod = function() {
        // TODO should we get this from the server?

        var period = this._getIntFromElm('#period');

        // At the beginning of the game, we display Just Started.
        // If it is the beginning the period number is 0.
        if (isNaN(period)) {
            return 0;
        } else {
            return period;
        }
    };

    /**
     * Modifies inventory
     * @param {integer} delta Amount positive or negative by which to change inventory.
     */
    GameUI.prototype.modInv = function(delta) {
        var elm = $('#inv-amt'), amt = this._getIntFromElm(elm);
        elm.text(amt+delta);
    };

    /**
     * Get the text of an element and convert it to an integer.
     * @param {string or jQuery object} selector The jQuery selector or jQuery object of an element.
     * @returns {integer} The text value of the element converted to an integer.
     */
    GameUI.prototype._getIntFromElm = function(selector) {
        if (selector instanceof jQuery) {
            return parseInt(selector.text(), 10);
        }
        return parseInt($(selector).text(), 10);
    };

    function Admin(opts) {
        this.opts = opts;
    }

    // Beergame controls the game play by communicating with the
    // server and controlling the overall flow of the game.
    function Beergame (opts) {
    }

    Beergame.prototype.init = function() {
        var self = this;

        this.ui = new GameUI();

        var locPath = location.pathname.split('/'), params, that = this;
        this.gameSlug = locPath[2];
        this.role = locPath[3];
        this.currentPeriod = this.ui.getPeriod();
        this.periodObj = null;


        this.BUTTONS = ['start-btn', 'step1-btn', 'step2-btn', 'ship-btn', 'step3-btn', 'order-btn'];
        this.currentBtn = 0; // index of BUTTONS

        this.initUI();

        $('.button').live('click', $.proxy(this.initButtonHandlers, this));

        $('#add-game-form').on('submit', function(evt) {
            evt.preventDefault();
            self.createGame();
        });

    };

    Beergame.prototype._buildUrl = function(gameSlug, role, currentPeriod) {
        var url = '/api/games/';
        if (gameSlug !== undefined) {
            url += gameSlug + '/';
        }
        if (role !== undefined) {
            url += 'players/' + role + '/';
        }
        if (currentPeriod !== undefined) {
            url += 'periods/' + currentPeriod + '/';
        }
        return url;
    };

    Beergame.prototype._getCurBtnId = function() {
        return this.BUTTONS[this.currentBtn];
    };

    Beergame.prototype.initButtonHandlers = function(evt) {
        console.log('button clicked...');
        var elm = evt.target;

        $(elm).attr('disabled', true);
        this.currentBtn = $.inArray(elm.id, this.BUTTONS);

        switch (elm.id) {
            case 'start-btn':
                console.log('clicked next period');
                this.nextPeriod();
            break;
            case 'step1-btn':
                console.log('clicked step1');
                this.step1();
            break;
            case 'step2-btn':
                console.log('clicked step2');
                this.step2();
            break;
            case 'ship-btn':
                console.log('clicked ship');
                this.ship();
            break;
            case 'step3-btn':
                console.log('clicked step3');
                this.step3();
            break;
            case 'order-btn':
                console.log('clicked order');
                this.order();
            break;
        }
    };

    Beergame.prototype.initUI = function() {
        $('.button').attr('disabled', true);
        var that = this;
        this.doAjax(this._buildUrl(this.gameSlug, this.role), 'GET', '', '', function(data, textStatus, xhr) {
            that.playerObj = data;

            if (data.state === 'not_started') {
                that.currentBtn = 0;
            } else {
                that.currentBtn = $.inArray(data.current_state + '-btn', that.BUTTONS) + 1;
            }

            $('#' + that._getCurBtnId()).attr('disabled', false);
        }, function() {});
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
        if ((method === 'POST' || method === 'PUT') && data === '') {
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

    Beergame.prototype.doBtnAjax = function(url, method, data, dataType, callback) {
        console.log('in doBtnAjax');

        function sCallback(data, textStatus, xhr) {
            console.log('in btnAjax success callback');
            this.currentBtn += 1;
            curBtnId = this._getCurBtnId();
            console.log('curBtnId: ' + curBtnId);
            $('#'+this._getCurBtnId()).attr('disabled', false);

            callback(data, textStatus, xhr);
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
        var that = this, nameElm = $('#id_group_name'), groupName = nameElm.val(),
            numPeriods = $('#id_num_periods').val(),
            data = JSON.stringify({
                        group_name: groupName,
                        num_periods: numPeriods
                    });

        this.doAjax('/api/games/', 'POST', data, 'text', function(data, textStatus, xhr) {
            // clear group name
            nameElm.val('');
            that._addGame();
        });
    };

    Beergame.prototype.nextPeriod = function() {
        // create next period object
        var that = this;
        this.doBtnAjax(this._buildUrl(this.gameSlug, this.role) + 'periods/', 'POST', '', 'text', function(data, textStatus, xhr) {
            console.log(textStatus);
            that.incrPeriod();
        });
    };

    Beergame.prototype.advanceShipments = function() {
        this.doAjax(this._buildUrl(this.gameSlug, this.role, this.currentPeriod), 'GET', '', 'json', function(data, textStatus, xhr) {
            this.periodObj = data;

            $('#inv-amt').text(data.inventory);
            $('#ship1-amt').text(data.shipment_1);

            if (data.shipment_2 === null) {
                $('#ship2-amt').text('waiting...');
            }
        });
    };

    Beergame.prototype.step1 = function() {
        // advance shipments towards inventory
        var that = this;
        this.doBtnAjax(this._buildUrl(this.gameSlug, this.role, this.currentPeriod) + '?step=1',
                        'PUT', '', 'text', function(data, textStatus, xhr) {
            that.advanceShipments();
        });
    };

    Beergame.prototype.advanceOrders = function() {
        this.doAjax(this._buildUrl(this.gameSlug, this.role, this.currentPeriod), 'GET', '', 'json', function(data, textStatus, xhr) {
            this.periodObj = data;

            $('#order-amt').text(data.demand);
        });
    };

    Beergame.prototype.step2 = function() {
        // advance orders towards current order
        var that = this;
        this.doBtnAjax(this._buildUrl(this.gameSlug, this.role, this.currentPeriod) + '?step=2',
                        'PUT', '', 'text', function(data, textStatus, xhr) {
            that.advanceOrders();
        });
    };

    Beergame.prototype.ship = function() {
        // ship to downstream
        var self = this, downStreamRole = this._getDownStreamRole(this.role),
            shipment = $('#amt-to-ship').val(), data;

        data = JSON.stringify({
                                shipment_2: shipment
                            });
        this.doBtnAjax(this._buildUrl(this.gameSlug, downStreamRole, this.currentPeriod) + '?step=ship',
                        'PUT', data, 'text', function(data, textStatus, xhr) {
            self.ui.modInv(-shipment);
        });
    };

    Beergame.prototype.step3 = function() {
        var self = this;

        this.doBtnAjax(this._buildUrl(this.gameSlug, this.role, this.currentPeriod) + '?step=3',
                        'PUT', '', 'text', function(data, textStatus, xhr) {
            self.doBtnAjax('/g/html/' + '?template=period_listing&game_slug=' + self.gameSlug + '&role=' + self.role,
                            'GET', '', 'text', function(data, textStatus, xhr) {
                $('#period-table').html(data);
            });
        });
    };

    Beergame.prototype.order = function() {
        var that = this, order = $('#amt-to-order').val(), data;

        data = JSON.stringify({ order_2: order });

        this.doBtnAjax(this._buildUrl(this.gameSlug, this.role, this.currentPeriod) + '?step=order',
                        'PUT', data, 'text', function(data, textStatus, xhr) {
            // TODO do we need to do anything after we order?
            // Yes, wait for the other teams to finish!
        });

    };

    Beergame.prototype.incrPeriod = function() {
        var per = $('#period');
        this.currentPeriod += 1;

        per.text(this.currentPeriod);
    };

    Beergame.prototype._getDownStreamRole = function(role) {
        var ROLES = ['factory', 'distributor', 'wholesaler', 'retailer'], curIndex, nextIndex;

        curIndex = $.inArray(role, ROLES);
        nextIndex = curIndex + 1;

        if (nextIndex != ROLES.length) {
            return ROLES[nextIndex];
        } else {
            return role;
        }
    };

    Beergame.prototype._getUpStreamRole = function(role) {
        var ROLES = ['factory', 'distributor', 'wholesaler', 'retailer'], curIndex, prevIndex;

        curIndex = $.inArray(role, ROLES);
        prevIndex = curIndex - 1;

        if (prevIndex >= 0) {
            return ROLES[prevIndex];
        } else {
            return role;
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
