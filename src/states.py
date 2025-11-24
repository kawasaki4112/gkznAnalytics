from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    waiting_for_social_category = State()
    waiting_for_assessment_service = State()
    waiting_for_assessment_score = State()
    waiting_for_assessment_comment = State()
    waiting_for_username = State()
    waiting_for_reset_confirmation = State()
    
class ServiceStates(StatesGroup):
    waiting_for_service_name = State()
    waiting_for_service_import = State()

class SpecialistStates(StatesGroup):
    waiting_for_specialist_fio = State()
    waiting_for_specialist_organization = State()
    waiting_for_specialist_department = State()
    waiting_for_specialist_position = State()
    waiting_for_specialist_import = State()
    waiting_for_search_query = State()
    
class SpamStates(StatesGroup):
    waiting_for_spam_text = State()
    waiting_for_spam_confirmation = State()
    
class CategoryStates(StatesGroup):
    waiting_for_category_import = State()
    waiting_for_category_name = State()
    waiting_for_category_deletion = State()
    
class SubCategoryStates(StatesGroup):
    waiting_for_subcategory_name = State()
    waiting_for_subcategory_deletion = State()