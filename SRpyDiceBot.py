import smtplib, email, imaplib, os, re, random, msvcrt, time
from email.mime.text import MIMEText

#SEND REPLY EMAIL---------------------------------------------------------------------------------------	
	
def sendMail(email_body, email_subject, email_messageid) :
	user = ''
	pwd = ''
	group = ''

	#Initialize the message container
	msg = MIMEText(email_body)
	msg['Subject'] = email_subject
	msg['Message-ID'] = email_messageid
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
	hits = 0
	glitch = 0
	# Initialize variables representing:
	# 1. The number of dice to be rolled
	# 2. The type of dice to be rolled
	# 3. Any modifications to the roll
	try :
		m = re.match("@Roll ([1-9][0-9]?)D([1-9][0-9]?)\s?\+?\s?([1-9])?", dice_input)
		num_dice = m.group(1)
		type_dice = m.group(2)
		mod = m.group(3) 
		n = int(num_dice)
		each_roll = []
		# Seed the RNG with the current system time
		random.seed()
		total_roll = 0
		# Roll each die individually and add up the total
		t = n
		num = 0
		while t > 0 :
			each_roll.append(random.randint(1, int(type_dice)))
			total_roll = total_roll + each_roll[num]
			if (each_roll[num] == 5 or each_roll[num] == 6) :
				hits += 1
			if (each_roll[num] == 1) :
				glitch +=1
			num += 1
			t = t - 1
		#Return different messages depending on if this dice roll contained a modifier.
		t = n
		if (mod) :
			roll_message = num_dice + "D" + type_dice + " +" + mod + " = " + "("
			while t > 0:
				roll_message = roll_message + str(each_roll[t-1])
				if not (t == 1) :
					roll_message = roll_message + " + "
				else:
					roll_message = roll_message + ")" + " + " + str(int(mod))
				t = t - 1
			roll_message = roll_message + " = " + str((total_roll) + int(mod))
		else :
			roll_message = num_dice + "D" + type_dice + " = "
			while t > 0:
				roll_message = roll_message + str(each_roll[t-1]) 
				if not (t == 1) :
					roll_message = roll_message + " + "
				t = t - 1
			roll_message =  roll_message + " = " + str((total_roll))
		roll_message = roll_message + "\n\nNumber of Successes: " + str(hits)
		if (glitch > (int(num_dice) / 2)) :
			if (hits == 0) :
				roll_message = roll_message + "\nCritical Glitch!"
			else:
				roll_message = roll_message + "\nGlitch!"
		return roll_message
	except :
		return "\n\nDice roll was improperly formatted. Please format your dice roll request in the following form : \n XDY + Z where X, Y, are integers between 1-99 and Z is an integer between 0-9.\n\n"




		
# GET NEW EMAILS-----------------------------------------------------------------------------------------
def getMail() :
	# directory where to save attachments (default: current)
	detach_dir = '.'
	# Login = 
	# Password = 
	user = ''
	pwd = ''

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
	email_messageid = ""
	
	try:
		for emailid in items[0].split() :
			# fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
			resp, data = m.fetch (emailid, '(RFC822)') 
			for response_part in data :
				if isinstance(response_part, tuple) :
					msg = email.message_from_string(response_part[1])
					payload = msg.get_payload()
					email_body = extract_body(payload)
					##
					debugFile(email_body)
					##
					email_subject = msg['Subject']
					email_messageid = msg['Message-ID']
				typ, response = m.store(emailid, '+FLAGS', r'(\Seen)')
			
			if not msg['From'] == "pydicebot@gmail.com" :
				parseEmail(email_body, email_subject, email_messageid)
	finally:
		try:
			m.close()
		except:
			pass
		m.logout()
		
# Pulls apart the email object to get the actual email text.
def extract_body(payload) :
	if isinstance(payload, str) :
		return payload
	else :
		return '\n'.join([extract_body(part.get_payload()) for part in payload])
			
#Used for testing purposes only.
#Used for testing purposes only.
def debugFile(text) :
	f = open('debug.txt', 'w')
	f.write(text)
	f.close()
	
# Parse the email body string
def parseEmail(email_body, email_subject, email_messageid) :
	# If 1+ @Roll exists 
	if "@Roll" in email_body:
		# Create a message text to be sent as an email
		message = ""
		if "--You r" in email_body:
			regex = re.compile('(.*)--You r', re.DOTALL)
			match_body = regex.match(email_body)
			email_body = match_body.group(1)
		else:
			regex = re.compile('^@Roll .*\n', re.MULTILINE)
			match = regex.findall(email_body)
		# For each @Roll, perform dice roll, add results to message text
		for each_roll in match:
			message = message + rollDice(each_roll) + "\n"
		# Send email
		sendMail(message, email_subject, email_messageid)

#Main Body Loop
#	- Check new mail every X minutes.
while True :
	getMail()
	if msvcrt.kbhit() :
		break
	time.sleep(300)
	
