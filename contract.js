"use strict";

var DepositContent = function(text) {
    if (text) {
        var o = JSON.parse(text);
        this.balance = new BigNumber(o.balance);
        this.expiryHeight = new BigNumber(o.expiryHeight);
    } else {
        this.balance = new BigNumber(0);
        this.expiryHeight = new BigNumber(0);
    }
};

DepositContent.prototype = {
    toString: function() {
        return JSON.stringify(this);
    }
};

var RoomContract = function() {
    LocalContractStorage.defineMapProperty(this, "roomContract", {
        parse: function(text) {
            return new DepositContent(text);
        },
        stringify: function(o) {
            return o.toString();
        }
    });

};

// save value to contract, only after height of block, users can takeout
RoomContract.prototype = {
    init: function() {
    },

    checkIn: function(height) {
        var from = Blockchain.transaction.from;
        var value = Blockchain.transaction.value;
        var bk_height = new BigNumber(Blockchain.block.height);

        var orig_deposit = this.roomContract.get(from);
        if (orig_deposit) {
            value = value.plus(orig_deposit.balance);
        }

        var deposit = new DepositContent();
        deposit.balance = value;
        deposit.expiryHeight = bk_height.plus(height);

        this.roomContract.put(from, deposit);
    },

    checkOut: function(value) {
        var from = Blockchain.transaction.from;
        var bk_height = new BigNumber(Blockchain.block.height);
        var amount = new BigNumber(value);

        var deposit = this.bankVault.get(from);
        if (!deposit) {
            throw new Error("No deposit before.");
        }

        if (bk_height.lt(deposit.expiryHeight)) {
            throw new Error("Can not takeout before expiryHeight.");
        }

        var result = Blockchain.transfer(from, amount);
        if (!result) {
            throw new Error("transfer failed.");
        }
        Event.Trigger("RoomDeposit", {
            Transfer: {
                from: Blockchain.transaction.to,
                to: from,
                value: amount.toString()
            }
        });

        deposit.balance = deposit.balance.sub(amount);
        this.bankVault.put(from, deposit);
    },

    balanceOf: function() {
        var from = Blockchain.transaction.from;
        return this.bankVault.get(from);
    },

    verifyAddress: function(address) {
        // 1-valid, 0-invalid
        var result = Blockchain.verifyAddress(address);
        return {
            valid: result == 0 ? false : true
        };
    }
};

module.exports = RoomContract;