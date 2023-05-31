__author__ = "KTeymoury"
__copyright__ = "Copyright 2023"
__credits__ = ["Mehdi Roudaki", "Hamid Moradi"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = ""
__email__ = "kaveh.teymoury@gmail.com"
__status__ = "Production"

import datetime

from behave import given, when, then, step, use_step_matcher
from utils.my_log import MyLog
from app.db.base import Base
from app.model.record import Record
from app.model.patient import Patient
import names
import random

use_step_matcher("re")

database_handler = Base()
logger = MyLog()


@given('I have a medical record with token "(?P<token>.+)"')
def step_impl(context, token):
    """
    :type context: behave.runner.Context
    :type token: str
    """
    context.my_records = database_handler.my_db[Record.__name__]
    current_record = context.my_records.find_one({'token': token})
    if current_record:
        logger.log.info('Medical record found.')
    else:
        logger.log.info('Creating a dummy medical record for given private token.')
        dummy = Patient.make_dummy()
        patient_collection = database_handler.my_db[Patient.__name__]
        patient_record = patient_collection.find_one({'name': dummy.name,
                                                      'ssid': dummy.ssid})
        patient_id = None
        if patient_record:
            patient_id = patient_record['_id']
        else:
            patient_id = patient_collection.insert_one({'name': dummy.name, 'ssid': dummy.ssid}).inserted_id
        current_record = context.my_records.insert_one({
            'patient_id': patient_id,
            'token': token,
            'info': "You'll die soon mate",
            'date': datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M %p")
        })
        current_record = context.my_records.find_one({'_id': current_record.inserted_id})
    patient_record = database_handler.my_db[Patient.__name__].find_one({'_id': current_record['patient_id']})
    patient = Patient(name=patient_record['name'],
                      ssid=patient_record['ssid'],
                      id_cart=current_record['patient_id'])
    medical_record = Record(patient=patient,
                            token=current_record['token'],
                            info=current_record['info'],
                            date=current_record['date'].strftime("%Y-%m-%d %I:%M %p"))
    context.my_record = medical_record


@when('I open "Medical Records" section')
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    logger.log.info('You are looking at "Medical Records". Please enter your private token.')


@step("enter my private token")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    logger.log.info('Medical record retrieved successfully.')


@then("my medical record should be shown")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    logger.log.info(f'Token {context.my_record.token} corresponds to:'
                    f'\n\tPatient name: {context.my_record.patient.name}'
                    f'\n\tDate: {context.my_record.date}'
                    f'\n\tInformation: {context.my_record.info}')