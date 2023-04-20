import process
import final

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('현재 경로:', os.path.abspath('.'))

if __name__=='__main__':
    process.process()
    final.login_send()