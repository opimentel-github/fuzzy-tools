from __future__ import print_function
from __future__ import division
from . import _C

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

###################################################################################################################################################

def send_mail(receptor_email:str, email_dict:str,
	emisor_email:str='flaming.choripan@gmail.com',
	emisor_pass:str='choripan123',
	server:str='localhost',
	):
	'''
	email_dict: subject, content, images
	'''
	msg = MIMEMultipart()
	msg['Subject'] = email_dict['subject']
	msg['From'] = emisor_email
	msg['To'] = receptor_email

	msg.attach(MIMEText(email_dict['content']))

	images_filedirs = email_dict.get('images', [])
	for k,image_filedir in enumerate(images_filedirs):
		fp = open(image_filedir, 'rb')
		image = MIMEImage(fp.read(), name=os.path.basename(image_filedir))
		fp.close()
		msg.add_header('Content-ID', f'<image{k}>')
		msg.attach(image)

	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(emisor_email, emisor_pass)
	s.sendmail(emisor_email, receptor_email, msg.as_string())
	s.quit()