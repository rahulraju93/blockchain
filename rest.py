from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
import subprocess
from subprocess import Popen, PIPE
import re
from string import printable
import requests
import json
import time


app = Flask(__name__)
api = Api(app)

from_wallet = "n1FF1nz6tarkDVwWQkMnnwFPuPKUaQTdptE"
global_contract_addr = "n1qMx7NDgq75tiRYWfXzUq1BnvEKAKWPzTL"
#to_wallet = "n1Z3ybkR1UE7eVh53SEDT5fctLaRoNyYBUJ"

def global_nounce(from_wallet_ = from_wallet):
	payload_from = {"address":from_wallet_}
	r_from = requests.post("http://localhost:8685/v1/user/accountstate", data=json.dumps(payload_from))
	r_from = r_from.json()
	nounce_from = r_from['result']['nonce']
	#print "nounce_from, nounce_to : ", nounce_from, nounce_to
	return nounce_from

def deploy_contract(temp = 5):
	n_f = global_nounce()
	payload= {"transaction": {"from":from_wallet,"to":from_wallet, "value":"0","nonce":int(n_f) + 1,"gasPrice":"1000000","gasLimit":"2000000","contract":{"source":"\"use strict\";var DepositeContent=function(text){if(text){var o=JSON.parse(text);this.balance=new BigNumber(o.balance);this.expiryHeight=new BigNumber(o.expiryHeight);}else{this.balance=new BigNumber(0);this.expiryHeight=new BigNumber(0);}};DepositeContent.prototype={toString:function(){return JSON.stringify(this);}};var BankVaultContract=function(){LocalContractStorage.defineMapProperty(this,\"bankVault\",{parse:function(text){return new DepositeContent(text);},stringify:function(o){return o.toString();}});};BankVaultContract.prototype={init:function(){},save:function(height){var from=Blockchain.transaction.from;var value=Blockchain.transaction.value;var bk_height=new BigNumber(Blockchain.block.height);var orig_deposit=this.bankVault.get(from);if(orig_deposit){value=value.plus(orig_deposit.balance);} var deposit=new DepositeContent();deposit.balance=value;deposit.expiryHeight=bk_height.plus(height);this.bankVault.put(from,deposit);},takeout:function(value){var from=Blockchain.transaction.from;var bk_height=new BigNumber(Blockchain.block.height);var amount=new BigNumber(value);var deposit=this.bankVault.get(from);if(!deposit){throw new Error(\"No deposit before.\");} if(bk_height.lt(deposit.expiryHeight)){throw new Error(\"Can not takeout before expiryHeight.\");} if(amount.gt(deposit.balance)){throw new Error(\"Insufficient balance.\");} var result=Blockchain.transfer(from,amount);if(!result){throw new Error(\"transfer failed.\");} Event.Trigger(\"BankVault\",{Transfer:{from:Blockchain.transaction.to,to:from,value:amount.toString()}});deposit.balance=deposit.balance.sub(amount);this.bankVault.put(from,deposit);},balanceOf:function(){var from=Blockchain.transaction.from;return this.bankVault.get(from);},verifyAddress:function(address){var result=Blockchain.verifyAddress(address);return{valid:result==0?false:true};}};module.exports=BankVaultContract;","sourceType":"js", "args":""}}, "passphrase": "passphrase"} 

	r=requests.post("http://localhost:8685/v1/admin/transactionWithPassphrase", data=json.dumps(payload))
	c_r = r.json()
	c_r_tx = c_r['result']['txhash']
	c_r_addr = c_r['result']['contract_address']

	
	cr_flag = validate_contract(c_r_tx)
	#print "self.c_r_tx, self.c_r_addr, flag : ", self.c_r_tx, self.c_r_addr, cr_flag
	#global_contract_addr = c_r_addr
	return c_r_tx, c_r_addr, cr_flag

def validate_contract(con):
	payload= {"hash" : str(con)}
	r=requests.post("http://localhost:8685/v1/user/getTransactionReceipt", data=json.dumps(payload))

	v_c = r.json()
	if v_c['result']['status'] != 1:
		time.sleep(60)
		if v_c['result']['status'] != 1:
			return False

	return True

class Balance(Resource):
	def balance(self):
		b_payload_from = {"address":from_wallet}
		b_r_from = requests.post("http://localhost:8685/v1/user/accountstate", data=json.dumps(b_payload_from))
		b_r_from = b_r_from.json()
		balance_from = b_r_from['result']['balance']
		return balance_from
		
	def get(self):
		b = self.balance()
		return {"balance_of_user": b}

class Nounce(Resource):
	def nounce(self):
		payload_from = {"address":from_wallet}
		r_from = requests.post("http://localhost:8685/v1/user/accountstate", data=json.dumps(payload_from))
		r_from = r_from.json()
		nounce_from = r_from['result']['nonce']

		#print "nounce_from, nounce_to : ", nounce_from, nounce_to
		return nounce_from

	def get(self):
		b = self.nounce()
		return {"nounce_of_user": b}

class DeployContract(Resource):
	def get(self):
		tx,addr,flag = deploy_contract()
		return {"hash_of_transaction": tx, "address_of_transaction": addr, "flag_of_transaction": flag}

class CheckIn(Resource):
	def checkIn(self):
		"""
		Takes the information provided from the hotel and uses it to deploy a smart contract associated with
		the user's wallet. It transfers money after checking balance (two txns: deposit, rental/night). 
		"""
		n_f = global_nounce()
		if global_contract_addr != None:
			payload= {"transaction":{"from":from_wallet,"to":global_contract_addr, "value":"250","nonce":int(n_f) + 1,"gasPrice":"1000000","gasLimit":"2000000","contract":{"function":"save","args":"[0]"}}, "passphrase": "passphrase"}

			r=requests.post("http://localhost:8685/v1/admin/transactionWithPassphrase", data=json.dumps(payload))
			chk_in = r.json()
			#print "chk_in : ", chk_in
			self.chk_in_tx = chk_in['result']['txhash']

			c_in_flag = self.validate_txn(self.chk_in_tx)

		#print "self.chk_in_tx, self.chk_in_addr, flag : ", self.chk_in_tx, self.chk_in_addr, c_in_flag

			return self.chk_in_tx, c_in_flag
		else:
			return 0,0

	def validate_txn(self, txn):
		payload= {"hash" : str(txn)}
		r=requests.post("http://localhost:8685/v1/user/getTransactionReceipt", data=json.dumps(payload))

		v_c = r.json()

		if v_c['result']['status'] == 1:
			return "Validated"

		if v_c['result']['status'] == 2:
			return "Pending"

		if v_c['result']['status'] == 1:
			return "Failed"

		return "No Status"

	def get(self):
		tx,flag = self.checkIn()
		return {"hash_of_transaction": tx, "flag_of_transaction": flag}


class CheckOut(Resource):
	def checkOut(self):
		"""
		Returns the deposit back to the user from another wallet. The ID is removed from the secure list. 
		"""
		n_f = global_nounce()
		if global_contract_addr != None:
			payload= {"transaction":{"from":from_wallet,"to":global_contract_addr, "value":"0","nonce":int(n_f) + 1,"gasPrice":"1000000","gasLimit":"2000000","contract":{"function":"takeout","args":"[50]"}}, "passphrase": "passphrase"}

			r=requests.post("http://localhost:8685/v1/admin/transactionWithPassphrase", data=json.dumps(payload))

			chk_out = r.json()
			self.chk_out_tx = chk_out['result']['txhash']
			
			c_out_flag = self.validate_txn(self.chk_out_tx)

			#print "self.chk_out_tx, self.chk_out_addr, c_out_flag : ", self.chk_out_tx, self.chk_out_addr, c_out_flag

			return self.chk_out_tx, c_out_flag
		else:
			return 0, "No Status"

	def validate_txn(self, txn):
		payload= {"hash" : str(txn)}
		r=requests.post("http://localhost:8685/v1/user/getTransactionReceipt", data=json.dumps(payload))

		v_c = r.json()
		
		if v_c['result']['status'] == 1:
			return "Validated"

		if v_c['result']['status'] == 2:
			return "Pending"

		if v_c['result']['status'] == 1:
			return "Failed"

		return "No Status"

	def get(self):
		tx,flag = self.checkOut()
		return {"hash_of_transaction": tx, "flag_of_transaction": flag}


api.add_resource(CheckIn, '/checkIn')
api.add_resource(CheckOut, '/checkOut')
api.add_resource(Balance, '/balance')
api.add_resource(Nounce, '/nounce')
#api.add_resource(DeployContract, '/deploy')


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5040, debug=True)