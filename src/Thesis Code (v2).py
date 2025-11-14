#!/usr/bin/env python
# coding: utf-8


def create_directory(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def does_file_exist(path):
    return os.path.isfile(path)

def write_to_file(path,data):
   with open(path, 'a') as file:
        file.write(data + '\n')

def create_new_file(path):
    f = open(path,'w')
    f.write("")
    f.close()

def get_details(directory, url):
    driver.get(url)
    title = driver.find_element_by_class_name('post-title')
    print('\nTitle \n')
    write_to_file(directory + '/articles.txt', "\n Title: \n")
    print(str(title.text))
    write_to_file(directory + '/articles.txt', title.text)
    try:
        paragraphs = driver.find_element_by_class_name('tz-paragraph')
        print('\nParagraphs \n')
        write_to_file(directory + '/articles.txt', "\n Paragraphs: \n")
        print(str(paragraphs.text))
        write_to_file(directory + '/articles.txt', paragraphs.text)
    except NoSuchElementException:
        print('\nParagraphs \n')
        write_to_file(directory + '/articles.txt', "\n Paragraphs: \n")
        print('Empty')
        write_to_file(directory + '/articles.txt', '\n Empty \n')
    try:
        comments = driver.find_elements_by_class_name('reply-detail')
        print('\nComments \n')
        write_to_file(directory + '/articles.txt', "\n Comments: \n")
        for comment in comments:
            print(str(comment.text) + '\n')
            write_to_file(directory + '/articles.txt', comment.text)
    except NoSuchElementException:
        print('\nComments \n')
        write_to_file(directory + '/articles.txt', "\n Comments: \n")
        print('Empty')
        write_to_file(directory + '/articles.txt', "\n Empty \n")
    try:
        subcomments = driver.find_elements_by_class_name('reply-sub-front')
        print('\nSubComments \n')
        write_to_file(directory + '/articles.txt', "\n SubComments: \n")
        for subcomment in set(subcomments):
            print(str(subcomment.text) + '\n')
            write_to_file(directory + '/articles.txt', subcomment.text)
    except NoSuchElementException:
        print('\nSubComments \n')
        write_to_file(directory + '/articles.txt', "\n SubComments: \n")
        print('Empty')
        write_to_file(directory + '/articles.txt', "\n Empty \n")
    driver.close()
    

def main_scraper(url,directory):
    driver.get(url)
    continue_link = driver.find_element_by_tag_name('a')
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in set(elems):
        if 'thread' and '6830271' in str(elem.get_attribute("href")):
            print("url: " + elem.get_attribute("href"))
            elem_formatted = "url: " + elem.get_attribute("href")
            if does_file_exist(directory + "/articles.txt") is False:
                create_new_file(directory + "/articles.txt")
            write_to_file(directory + '/articles.txt', elem_formatted)
            get_details(directory, elem.get_attribute("href"))
        elif 'thread' and '6830286' in str(elem.get_attribute("href")):
            print("url: " + elem.get_attribute("href"))
            elem_formatted = "url: " + elem.get_attribute("href")
            if does_file_exist(directory + "/articles.txt") is False:
                create_new_file(directory + "/articles.txt")
            write_to_file(directory + '/articles.txt', elem_formatted)
            get_details(directory, elem.get_attribute("href"))
        else:
            continue



main_scraper('http://club.autohome.com.cn/bbs/forum-c-5769-1.html#pvareaid=3454448','ModelYAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6404-1.html#pvareaid=2108152','LYRIQAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6035-1.html#pvareaid=2108152','ID-6XAutoHomeBlog')


main_scraper('https://club.autohome.com.cn/bbs/forum-c-6029-1.html#pvareaid=3454448','MustangMach-EAutoHomeBlog')



words_list = ('年', '老', '岁','现代','过去', '最近', '曾经', '未来', '当前', '传统','目前', '如今','潮流', '趋势', '男', '女', '她', '他' ,'教育', '研究', '书','老师','教授', '专业', '毕业','领域','学', '课' ,'妻子', '丈夫', '老公',  '老婆','配偶','结婚','已婚', '离婚','单身','工作', '职位','职业', '事业', '上班','下班', '加班', '同事', '老板', '退休', '经理', '录用','招募','下岗', '收入', '工资', '穷', '钱', '赚', '挣', '元','经济', '贷款', '预算', '家庭', '物业', '住', '居' ,'房', '楼主' , '家人', '家族', '爸', '妈', '姐姐', '妹妹', '弟弟','哥哥', '奶奶', '爷爷', '外公', '外婆', '孩', '宝宝', '娃', '歧视', '家里','拥有','驾照','执照', '车主', '人口','城区', '市区', '农村', '气候', '变暖', '环境','环保','污染', '地球', '天空', '天气', '全球','行动', '缓解', '自然', '再生',  '影响', '作用','健康', '燃料', '承担', '干净', '大气', '回收' ,'主动', '节能','足够', '动作', '世界' , '意识', '症', '病', '风景', '电动',  '合作', '协调', '配合', '良心', '发展' , '开发', '空气', '碳','排放','减排','排气', '薄雾', '酸',' 电池', '垃圾','温度', '土', '绿色', '能源', '电源', '油耗', '油', '消耗', '自动', '手动', '电网', '供电', '电力', '变压器', '路程', '旅程','旅行', '行程', '旅游', '距离', '远', '近', '范围', '离开', '到达', '公里', '米', '英里', '千瓦时', '停止','速度','快','慢', '秒', '减速', '迅速', '加速', '平均', '踏板','续航', '寿命', '随车充', '尺寸', '大小', '寸', '大', '小', '充电', '维护', '保养', '熄火', '维修', '置换', '故障', '检查',  '稳定', '可靠','爆胎', '状态', '毛病', '噪音', '响', '安静', '声音',  '舒适', '适应', '舒服', '合适', '适合', '调节', '调整',' 操作', '运行', '运营', '出行', '简单', '难', '复杂', '容易', '熟练', '开车', '打开', '驾车' ,'驱动', '安全','危险', '质保', '伤害', '保险', '标准', '意外','事故', '品牌', '商标','牌子', '特斯拉', '大众汽车', '福特', '卡迪拉克', '外国', '本地','款', '国际', '流行','相同', '分别', '识别', '认可', '紧凑', '标志', '出口','进口','欢迎', '吸引', '智能', '不同', '纯电', '车型', '系列', '升级', '主流', '版', '时尚' , '新能源', '模型', '混合','组合','区别','差别', '差距', '质量', '高级', '旧', '新', '高端' , '评论', '评价', '改进', '改善','好', '不好', '素质', '品质',  '缺点', '优点',  '有用', '爱', '理想',  '喜欢', '独特','先进','基本', '平稳','坏', '价值', '值得', '棒', '进步', '特别', '普通', '一般', '嫌', '精彩', '完美', '保值', '优势', '积极', '消极','降级',  '设计', '辅助', '灵敏', '模式', '实际', '灵活', '颜色', '特点', '黑色', '白色', '功能', '红色', '蓝色', '紫色', '黄色', '质感', '帅', '空间', '丑', '车友','外观','内部','车窗', '增强', '引擎',  '轮胎', '内燃机' , '后备箱', '装置', '柔软', '座椅','灯','按钮', '屏', '按键', '配备', '美', '通风', '显示', '配置', '镜', '侧面','配件', '魅力', '漂亮', '空调', '前脸','流畅', '玩意', '内饰', '向盘','照明','刹车','车身', '外面','里面', '装', '车漆','材料','制动', '车顶', '车门', '仪表板','车轮', '玻璃','导航', '风格','马力' , '动力', '势力', '实力', '力量', '容量','性能', '表现', '效率', '较', '功率','有效', '相比', '对比', '价钱','报价','价格', '购置', '涨价', '付','买', '飙升', '采购', '成本', '贵', '高昂', '便宜','购车', '省钱',  '费', '换电', '储存', '电量','能耗', '锂','耗电', '发电',  '技术' , '店', '销售', '渠道','直接','签','订单', '额度', '销量', '沟通','交流','可用', '单纯', '及时', '得到','获得', '条件' ,'机会', '便利', '方便', '便捷', '禁止', '提车', '服务','售后', '广告', '公告', '网上','宣传','媒体', '信息, ', '消息', '记录', '明白', '清晰',  '清楚', '明确', '明显', '显然', '文章', '电影', '形象', '图片', '模糊', '数据', '发布', '提升','照片', '夸张', '表达','表示', '展示' , '展厅' , '平台', '知识', '知道', '税', '政策', '政府', '补贴', '优惠',  '停车',  '泊车', '权利', '车库', '驾驶', '行驶',  '基础', '充电站', '桩', '担心', '关心', '焦虑','着急','发愁', '没电', '电缆', '经验', '接触', '经历', '记忆', '记得', '体验','试驾', '测试', '试验', '考验', '了解', '理解','礼貌','对待', '尊重', '正式', '气氛', '氛围', '厂商', '匹配', '数量', '推出',  '制造',  '产', '市场', '转让', '合同', '使用', '利用',  '控制', '操控',  '自己', '自我',  '我', '本身', '身份','感受', '处理', '需要', '必要', '必须', '愿望',  '需求', '情绪', '反应', '强迫', '兼容',  '肯定',  '感觉',  '心理' ,'觉得', '反对', '拒绝', '计划', '规划', '打算', '感到', '采用',  '信心', '行为','投入', '问题', '解决', '幸福', '艰难', '高兴', '强制', '确认', '证明', '轻松', '坚持', '支持',  '放松', '确定','决定', '愿意', '决心', '精神', '忘记', '合理', '累', '认真', '真心', '享受', '兴趣','诚心', '概念','相信', '认知', '快乐', '麻烦', '失望', '希望', '吃惊' ,'兴奋','刺激', '印象', '深刻', '意见', '自由', '观点','想法', '建议', '考虑', '意义', '实用', '热情','认识','认出','满意','满足', '规范', '符合',  '朋友', '压力', '听说', '社会', '个人', '共识', '自主', '小区', '同意', '面子','国', '州', '省', '运动', '法律' ,'合法', '允许', '通过', '案例', '规则', '法规','鼓励','参加', '参与', '活动', '推荐', '分享', '咨询', '联系','关系', '民众','大众', '共同',  '责任', '负责', '义务',  '接纳', '接受','开放', '习惯', '改变', '变化', '变革', '付款', '折扣', '打折', '降价','奖励', '收获', '确保', '保障', '成员', '协会', '会员', '注册','包含', '包括', '回扣')



def main_download(directory):
    workbook = xlsxwriter.Workbook(directory + '.xlsx')
    worksheet = workbook.add_worksheet()
    file = open(directory + "/articles.txt", 'r')
    data = file.read()
    list1 = words_list
    d = "url"
    newlines = (data.split(d))
    t=0
    for line in newlines:
        t=t+1
        col = 0
        row = t
        worksheet.write(row, col, t)
        print('observation:' + str(t))
        row = 0
        col = 0
        for word in list1:
            col = col+1
            worksheet.write(row, col, word)
    for line in newlines:
        row = row + 1
        col = 1
        for word in list1:
            counts = line.count(word)
            worksheet.write(row, col, counts)
            col = col + 1
            print(word +':'+str(counts))
        continue
    workbook.close()

main_download('ModelYAutoHomeBlog')


main_download('LYRIQAutoHomeBlog')


main_download('ID-6XAutoHomeBlog')


main_download('MustangMach-EAutoHomeBlog')

