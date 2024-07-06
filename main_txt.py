# 请运行这个文件！其他文件请不要单独运行哦
print('\nInitializing...')
import os
import sys
os.chdir(sys.path[0])
from tqdm import tqdm
from chain_tool import get_overall_chain
import warnings
warnings.filterwarnings('ignore')

print("""Data source: user_input.txt""")

# 读取 user_input.txt 文件
with open('user_input.txt', 'r') as file:
    user_input_lines = file.readlines()
    
start, end = None, 2
    
# 提取关键词，生成 user_comments
left_idx = [idx for idx, line in enumerate(user_input_lines) if line == '原文：\n'][start:end]
right_idx = [idx for idx, line in enumerate(user_input_lines) if '拟回复：' in line][start:end]

try:
    user_comments = [''.join(user_input_lines[left + 1: right]) for left, right in zip(left_idx, right_idx)]
except:
    raise Exception('user_input.txt 关键词没有对齐，导致无法生成 user_comments')

# 对每一个 user_comment，调用 API 服务，获得其生成的结果
feedback_origin = []
feedback_language = []
feedback_translation = []
feedback_reply = []
type_ai_template = []
type_ai_origin = []
except_idx = []

# log_txt 用于记录
log_txt = []

print('\n正在调用 API 服务，请稍等...\n\n工作辛苦，也一定要注意休息哦...')

if len(user_comments) > 0:
    # 伪惰性生成，如果有对象才生成
    overall_chain = get_overall_chain()

# 使用 tqdm 库来显示进度条
for i in tqdm(range(len(user_comments))):
    model_output = overall_chain({'original_complaint': user_comments[i]})
    feedback_origin.append(model_output)
    feedback_language.append(model_output['original_language'])
    feedback_translation.append(model_output['transform_translation'])
    feedback_reply.append(model_output['original_language_reply'])
    type_ai_template.append(model_output['most_likely_type'])
    type_ai_origin.append(model_output['most_likely_type_origin'])
    log_txt.append(str(model_output))

# 导出 original_output.txt
model_feedback_origin = '\n\n'.join(str(feedback_origin))
with open('original_output.txt', 'w') as file: 
    file.write(model_feedback_origin)

for i in reversed(range(len(left_idx))):
    user_input_lines.insert(left_idx[i] - 2, feedback_translation[i])
    user_input_lines.insert(left_idx[i] - 4, '\n原文语言：' + feedback_language[i] + '\n')
    user_input_lines.insert(right_idx[i] + 2, '问题类型：' + type_ai_origin[i] + ' 使用模板：' + type_ai_template[i] + '\n')
    user_input_lines.insert(right_idx[i] + 4, feedback_reply[i])

# 将新的 user_input_lines 写入 model_feedback.txt 文件
model_feedback_str = ''.join(user_input_lines)
with open('model_output.txt', 'w') as file: 
    file.write(model_feedback_str)
    
# 导出 log_txt.txt
with open('log_txt.txt', 'w') as f:
    f.write('\n\n'.join(log_txt))

print('\033[92m\n\nmodel_output.txt is done. \n\n ...Enjoy your life!...\n\033[0m')