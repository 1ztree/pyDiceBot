import smtplib, email, imaplib, os, re, random
from email.mime.text import MIMEText

#SEND REPLY EMAIL---------------------------------------------------------------------------------------	
	
def sendMail(email_body, email_subject): 
	user = 'pyDiceBot@gmail.com'
	pwd = 'l0cal0ffense'
	group = 'hotfixrpg@googlegroups.com'

	#Initialize the message container
	msg = MIMEText(email_body)
	msg['Subject'] = email_subject
	msg['From'] = user
	msg['To'] = group

	
	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(user,pwd)
	server.sendmail(user, group, msg.as_string())
	server.quit()
	
# ROLL DICE---------------------------------------------------------------------------------------------

def rollDice(dice_input) :
    # Initialize the modifier variable, so errors are not thrown
    mod = 0
    # Initialize variables representing:
    # 1. The number of dice to be rolled
    # 2. The type of dice to be rolled
    # 3. Any modifications to the roll
    m = re.match("@Roll ([1-9][0-9]?)D([1-9][0-9]*)\s\+?\s([1-9])?", dice_input)
    num_dice = m.group(1)
    type_dice = m.group(2)
    mod = m.group(3) 
    t = int(num_dice)
    # Seed the RNG with the current system time
    random.seed()
    total_roll = 0
    # Roll each die individually and add up the total
    while t > 0 :
        total_roll = total_roll + random.randint(1, int(type_dice))
        print total_roll
        t = t - 1
    #Return different messages depending on if this dice roll contained a modifier.
    if (mod) :
        return num_dice + "D" + type_dice + " +" + mod + " = " + str((total_roll) + int(mod))
    else :
        return num_dice + "D" + type_dice + " = " + str((total_roll))




		
# GET NEW EMAIL-----------------------------------------------------------------------------------------
def getMail() :
	# directory where to save attachments (default: current)
	detach_dir = '.'
	# Login = pyDiceBot@gmail.com
	# Password = l0cal0ffense
	user = 'pyDiceBot@gmail.com'
	pwd = 'l0cal0ffense'

	# connecting to the gmail imap server
	m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
	try:
		m.login(user,pwd)
	except imaplib.IMAP4.error:
		str("LOGIN FAILED!!!")
	# here you a can choose a mail box like INBOX instead
	m.select("inbox") 

	# Get all UNREAD emails.
	resp, items = m.search(None, 'UNSEEN')
	# getting the mail ids

	#For each new email :
	#	- Check for instances of @Roll
	#	- For each instance of @Roll, perform the random dice roll indicated.
	#	- If at least one instance of @Roll exists, compose an email to the group,	
	#		containing each requested dice roll.
	email_body = ""
	email_subject = ""
	try:
		for emailid in items[0].split() :
			# fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
			resp, data = m.fetch (emailid, '(RFC822)') 
			for response_part in data :
				if isinstance(response_part, tuple) :
					msg = email.message_from_string(response_part[1])
					payload = msg.get_payload()
					email_body = extract_body(payload)
					email_subject = msg['Subject']
				typ, response = m.store(emailid, '-FLAGS', r'(\Seen)')
	finally:
		try:
			m.close()
		except:
			pass
		m.logout()
	# getting the mail content
	# Parse the email body string
	# If 1+ @Roll exists 
	if "@Roll" in email_body:
	#if string.find(email_body, '@Roll') >= 0 :
		# Create a message text to be sent as an email
		message = "Dice Roll(s)! \n"
		if "--You r" in email_body:
			regex = re.compile('(.*)--You r', re.DOTALL)
			match_body = regex.match(email_body)
			email_body = match_body.group(1)
		regex = re.compile('^@Roll .*\n', re.MULTILINE)
		match = regex.findall(email_body)

		#m = re.findall('^@Roll .*\n', email_body)
		# For each @Roll, perform dice roll, add results to message text
		for each_roll in match:
			message = message + rollDice(each_roll) + "\n"
		# Send email
		sendMail(message, email_subject)
		# Else get next email
	else:
		pass

def extract_body(payload) :
	if isinstance(payload, str) :
		return payload
	else :
		return '\n'.join([extract_body(part.get_payload()) for part in payload])
			
def debugFile(text) :
	f = open('debug.txt', 'w')
	f.write(text)
	f.close()

#Main Body Loop
#	- Check new mail every X minutes.
getMail()
