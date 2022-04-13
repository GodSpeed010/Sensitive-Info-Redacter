from Leak_Searcher import Leak_Searcher

leak_searcher = Leak_Searcher(
    receiver_name='Bob',
    sender_email='abc@gmail.com',
    receiver_email='abc@gmail.com',
    cc_emails='',
    my_password='pass'
)

#relative path of the intended dir to scan
search_dir_rel_path = 'Project/test_data/'

leak_searcher.scan_dir_files(search_dir_rel_path)