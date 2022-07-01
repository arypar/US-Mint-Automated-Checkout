import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import send_webhook
import time
class mint:
    def __init__(self,task_id,status_signal,image_signal,product,profile,proxy,monitor_delay,start_time):
        self.status_signal,self.image_signal,self.product,self.profile,self.monitor_delay,self.start_time = status_signal,image_signal,product,profile,float(monitor_delay),start_time
        self.session = requests.Session()
        if proxy != False:
            self.session.proxies.update(proxy)
        self.product = self.product.upper()            
        if self.start_time != "":
            self.status_signal.emit({"msg":"Waiting for Start Time " + self.start_time,"status":"alt"})
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            while str(current_time) != self.start_time:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                time.sleep(0.5)
        self.status_signal.emit({"msg":"Starting","status":"normal"})
        profile = self.profile
        card_number = profile["card_number"]
        HEADERS = { 'Accept':'*/*',
        'Cache-Control':'no-cache',
        'Connection':'keep-alive',
        'DNT':'1',
        'referer':'https://google.com',
        'Pragma':'no-cache',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
         } 
        atc = "https://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/Cart-AddProduct?format=ajax"
        cart = "https://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/Cart-Show"
        submit = "https://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/COSummary-Submit"

        linkinput = "https://catalog.usmint.gov/quicksilver-" + self.product + ".html"
        global declinecount
        global checkoutcount

        self.status_signal.emit({"msg":"Creating Session","status":"normal"})
        s = requests.session()

        self.status_signal.emit({"msg":"Session Created","status":"normal"})

        atcdata = {
        "cartAction": "add",
        "pid": self.product,
        "cgid": "silver-dollars",
        "egc": "null",
        "navid": "",
        "Quantity": "1"
            }

        start_time = time.time()
        def addtocart():
            global color
            global now 
            global current_time
            global delay
            self.status_signal.emit({"msg":"Adding to Cart","status":"alt"})
            atcchecker = self.session.post(atc, atcdata, headers = HEADERS)
            if str(atcchecker) != "<Response [200]>":
                self.status_signal.emit({"msg":"Error Adding to Cart","status":"error"})
                delay = self.monitor_delay
                time.sleep(delay)
                addtocart()
            if atcchecker.text.find("Your Bag is Empty") > -1:
                self.status_signal.emit({"msg":"Error Adding to Cart","status":"error"})
                delay = self.monitor_delay
                time.sleep(delay)
                addtocart()
        addtocart()
        self.status_signal.emit({"msg":"Added To Cart","status":"carted"})
        def gotocart():
            global check
            check = self.session.get(cart)
            if str(check) != "<Response [200]>":
                self.status_signal.emit({"msg":"Error Going Cart","status":"error"})
                time.sleep(self.monitor_delay)
                gotocart()
        gotocart()
        
        soup = BeautifulSoup(check.text, 'html.parser')
        checkoutlink = soup.find("form", {"class": "checkout-billing address"})
        checkoutlinkfinal = checkoutlink.attrs["action"]
        soup = BeautifulSoup(check.text, 'html.parser')
        cartpage = soup.find("input", {"name": "dwfrm_billing_securekey"})
        billingsecure = cartpage.attrs["value"]
        soup = BeautifulSoup(check.text, 'html.parser')
        cartpage1 = soup.find("input", {"name": "dwfrm_singleshipping_securekey"})
        shippingsecure = cartpage1.attrs["value"]
        
        self.session.get("https://catalog.usmint.gov/on/demandware.store/Sites-USM-Site/default/Cart-ValidateBulkLimit")

        firstcheckoutdata = {
        "dwfrm_singleshipping_shippingAddress_addressFields_selectedAddressID": "newaddress",
        "dwfrm_singleshipping_shippingAddress_addressFields_firstName": profile["billing_fname"],
        "dwfrm_singleshipping_shippingAddress_addressFields_lastName": profile["billing_lname"],
        "dwfrm_singleshipping_shippingAddress_addressFields_phone": profile["billing_phone"],
        "dwfrm_singleshipping_shippingAddress_email": profile["shipping_email"],
        "dwfrm_billing_billingAddress_emailsource": "Website - Checkout",
        "dwfrm_singleshipping_shippingAddress_addressFields_address1": profile["shipping_a1"],
        "dwfrm_singleshipping_shippingAddress_addressFields_address2": profile["shipping_a2"],
        "dwfrm_singleshipping_shippingAddress_addressFields_city": profile["shipping_city"],
        "dwfrm_singleshipping_shippingAddress_addressFields_states_state": profile["shipping_state"],
        "dwfrm_singleshipping_shippingAddress_addressFields_zip": profile["shipping_zipcode"],
        "dwfrm_singleshipping_shippingAddress_addressFields_country": "US",
        "dwfrm_singleshipping_shippingAddress_isCreateAccountSelected": "false",
        "dwfrm_singleshipping_createAccount_password": "",
        "dwfrm_singleshipping_createAccount_passwordconfirm": "",
        "dwfrm_singleshipping_createAccount_question": "1",
        "dwfrm_singleshipping_createAccount_answer": "",
        "dwfrm_singleshipping_securekey": shippingsecure,
        "dwfrm_billing_securekey": billingsecure,
        "format": "ajax",
        "refresh": "shipping",
        "dwfrm_singleshipping_shippingAddress_applyShippingAddress":""}

        self.status_signal.emit({"msg":"Submitting Shipping","status":"normal"})
        def submitshipping():
            postshipping = self.session.post(checkoutlinkfinal.replace("Cart-Show", "COSummary-Start"), firstcheckoutdata)
            if str(postshipping) != "<Response [200]>":
                self.status_signal.emit({"msg":"Error Submitting Shipping","status":"error"})
                submitshipping()
        submitshipping()

        secondcheckoutdata = {
        "dwfrm_singleshipping_shippingAddress_useAsBillingAddress": "true",
        "dwfrm_billing_billingAddress_addressFields_selectedAddressID": "",
        "dwfrm_billing_billingAddress_addressFields_firstName": profile["billing_fname"],
        "dwfrm_billing_billingAddress_addressFields_lastName": profile["billing_lname"],
        "dwfrm_billing_billingAddress_addressFields_address1": profile["billing_a1"],
        "dwfrm_billing_billingAddress_addressFields_address2": profile["billing_a2"],
        "dwfrm_billing_billingAddress_addressFields_city": profile["billing_city"],
        "dwfrm_billing_billingAddress_addressFields_states_state": profile["billing_state"],
        "dwfrm_billing_billingAddress_addressFields_zip": profile["billing_zipcode"],
        "dwfrm_billing_billingAddress_addressFields_country": "US",
        "dwfrm_billing_billingAddress_addressFields_phone": profile["billing_phone"],
        "dwfrm_billing_billingAddress_email_emailAddress": profile["shipping_email"],
        "dwfrm_billing_securekey": billingsecure,
        "dwfrm_singleshipping_securekey": shippingsecure,
        "refresh": "payment",
        "format": "ajax",
        "dwfrm_billing_applyBillingAndPayment": "",
        "dwfrm_billing_paymentMethods_selectedPaymentMethodID": "CREDIT_CARD",
        "dwfrm_billing_paymentMethods_creditCard_type": profile["card_type"],
        "dwfrm_billing_paymentMethods_creditCard_owner": profile["billing_fname"] + " " + profile["billing_lname"],
        "dwfrm_billing_paymentMethods_creditCard_number": card_number,
        "dwfrm_billing_paymentMethods_creditCard_month": profile["card_month"],
        "dwfrm_billing_paymentMethods_creditCard_year": profile["card_year"],
        "dwfrm_billing_paymentMethods_creditCard_cvn": profile["card_cvv"],
        "dwfrm_billing_securekey": billingsecure
        }

        self.status_signal.emit({"msg":"Submitting Billing","status":"normal"})
        def submitbilling():
            postbilling = self.session.post(checkoutlinkfinal.replace("Cart-Show", "COSummary-Start"), secondcheckoutdata)
            if str(postbilling) != "<Response [200]>":
                self.status_signal.emit({"msg":"Error Submitting Billing","status":"error"})
                submitbilling()
        submitbilling()
        
        lastcheckoutdata = {
        "dwfrm_billing_paymentMethods_selectedPaymentMethodID": "CREDIT_CARD",
        "dwfrm_billing_paymentMethods_creditCard_type": profile["card_type"],
        "dwfrm_billing_paymentMethods_creditCard_owner": profile["billing_fname"] + " " + profile["billing_lname"],
        "dwfrm_billing_paymentMethods_creditCard_number": card_number,
        "dwfrm_billing_paymentMethods_creditCard_month": profile["card_month"],
        "dwfrm_billing_paymentMethods_creditCard_year": profile["card_year"],
        "dwfrm_billing_paymentMethods_creditCard_cvn": profile["card_cvv"],
        "dwfrm_billing_securekey": billingsecure,
        "dwfrm_emailsignup_phone":"" }

    
        self.status_signal.emit({"msg":"Submitting Order","status":"alt"})

        def submitorder():
            global gg
            gg = self.session.post(submit, lastcheckoutdata)
            if str(gg) != "<Response [200]>":
                self.status_signal.emit({"msg":"Error Submitting Order","status":"error"})
                submitorder()
        submitorder()
        end_time = time.time()
        time_lapsed = end_time - start_time

        if gg.text.find("We are sorry, but we are unable to process your payment and submit your order this time.") > -1:

            self.status_signal.emit({"msg":"Error at Checkout, Payment Declined","status":"error"})
            send_webhook("PF","US Mint",self.profile["profile_name"],task_id,str(time_lapsed))
   
    
        if gg.text.find("Thank you for your order") > -1:
    
            self.status_signal.emit({"msg":"Checkout Success!","status":"success"})
            send_webhook("OP","US Mint",self.profile["profile_name"],task_id, str(time_lapsed))
