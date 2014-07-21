import smtplib, email, imaplib, os, re, random

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
	num_dice, type_dice, mod = re.match("@Roll ([1-9])D([1-9][0-9]*) \+?([1-9])?", dice_input)
	# Seed the RNG with the current system time
	random.seed()
	total_roll = 0
	# Roll each die individually and add up the total
	while num_dice > 0 :
		total_roll = total_roll + random.randint(1, type_dice)
	#Return different messages depending on if this dice roll contained a modifier.
	if (mod != 0) :
		return num_dice + "D" + type_dice + " +" + mod + " = " + (total_roll + mod)
	else :
		return num_dice + "D" + type_dice + " = " + (total_roll + mod)
		
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
					debugFile("Email_Body\n" + email_body + '\n')
					email_subject = msg['Subject']
				typ, response = m.store(emailid, '+FLAGS', r'(\Seen)')
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
		m = re.findall('@Roll\w+\n', email_body)
		# For each @Roll, perform dice roll, add results to message text
		for each_roll in m:
			message = message + rollDice(each_roll) + "\n"
		# Send email
		sendMail(message, email_subject)
		# Else get next email
	else:
		pass

def extract_body(payload) :
	if isintance(payload, str) :
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
