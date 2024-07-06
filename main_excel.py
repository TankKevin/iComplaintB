# 请运行这个文件！其他文件请不要单独运行哦
print('\nInitializing...')
import pandas as pd
from tqdm import tqdm
from chain_tool import get_overall_chain
import warnings
warnings.filterwarnings('ignore')

print("""Data source: PR外投跟进数据.xls""")

# 模型返回可信度的最小阈值
threshold = 0.3

# 读取数据
pr_data = pd.read_excel('PR外投跟进数据_17186272075362024-06-17 12_26_50.xls')

# 处理人工打标
pr_data['外投问题类型(一级)'] = pr_data['外投问题类型(一级)'].map(lambda x: [xx.strip('问题') for xx in x.split(',')] if type(x) == str else [])
pr_data['外投问题类型(二级)'] = pr_data['外投问题类型(二级)'].map(lambda x: [xx.split('-')[0].strip('问题') + '>' + xx.split('-')[1] for xx in x.split(',')] if type(x) == str else [])

# 添加 AI 列
pr_data = pr_data.reindex(['Case Id', '外投问题类型(一级)', '外投问题类型(一级)_AI', '外投问题类型(二级)', '外投问题类型(二级)_AI', '用户原声', '渠道', '外投时间', '用户昵称/账号', '录入时间', '国家', '外投原因'], axis=1)

# 对每一行数据进行打标
print('\n正在调用 API 服务，请稍等...\n\n工作辛苦，也一定要注意休息哦...')

log_excel = []

if len(pr_data) > 0:
    # 伪惰性生成，如果有对象才生成
    overall_chain = get_overall_chain()

start, end = None, 50

for idx in tqdm(pr_data.index[start:end]):
    row = pr_data.loc[idx]

    input_text = row['用户原声']
    model_output = overall_chain({'original_complaint': input_text})
    log_excel.append(row['Case Id'] + ' ' + str(model_output))
    
    # 首先获得 level_2，然后获得 level_1
    level_2_ai = [problem_type for problem_type, likelyhood in zip(model_output['final_problem_types'], model_output['final_likehoods']) if likelyhood >= threshold]
    if not level_2_ai:
        level_2_ai = ['无具体投诉事项>无具体投诉事项']
    
    level_1_ai = pd.Series([l2.split('>')[0] for l2 in level_2_ai]).unique().tolist()
    
    # 将打标结果输入 DataFrame
    pr_data.loc[idx, '外投问题类型(一级)_AI'] = str(level_1_ai)
    pr_data.loc[idx, '外投问题类型(二级)_AI'] = str(level_2_ai)

pr_data.to_excel('PR外投跟进数据_AI.xlsx')
with open('log_excel.txt', 'w') as f:
    f.write('\n\n'.join(log_excel))