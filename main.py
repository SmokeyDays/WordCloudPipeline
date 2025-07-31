# -*- coding: utf-8 -*-

import os
import jieba
import translators as ts
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import re # 确保在脚本顶部导入 re 模块


# --- 配置区 ---

# 1. 设置数据目录
DATA_DIR = './data/'
STOPWORDS_PATH = './special_words/baidu_stopwords.txt'
ADHOCWORDS_PATH = './special_words/adhocwords.txt'

# 2. ！！！【重要】请务必设置正确的中文字体路径！！！
#    - Windows: 'C:/Windows/Fonts/msyh.ttc' (微软雅黑) or 'C:/Windows/Fonts/simhei.ttf' (黑体)
#    - macOS: '/System/Library/Fonts/PingFang.ttc' (苹方)
#    - Linux: '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc' (思源黑体)
#    - 或者您下载的任何 .ttf/.otf 字体文件的路径
FONT_PATH = 'C:/Windows/Fonts/msyh.ttc'  # <--- 修改这里

# 3. 设置词云参数
MAX_WORDS = 100  # 词云中显示的最大词数
WIDTH = 1000     # 图片宽度
HEIGHT = 800     # 图片高度
BACKGROUND_COLOR = "white"  # 背景颜色

# 4. 中文停用词列表 (可根据需要扩展)
#    我们在这里排除单字和一些常见助词、连词等
# STOPWORDS = {'的', '是', '了', '在', '也', '和', '就', '都', '我', '你', '他', '她', '它', '我们', '你们', '他们', '一种', '这个', '那个', '一个'}

def load_words(path):
    d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    filepath = os.path.join(d, path)
    return [line.strip() for line in open(filepath, encoding='utf-8').readlines()]

def load_stopwords(stopwords_path = STOPWORDS_PATH):
    stopwords = set(load_words(stopwords_path))
    stopwords.update(STOPWORDS)
    return stopwords

def load_adhocwords(adhocwords_path = ADHOCWORDS_PATH):
    adhocwords = set(load_words(adhocwords_path))
    return adhocwords

def add_words(words):
    for item in words:
        jieba.add_word(item)

def remap_translation(raw_translation):
    adhoc_translation = {
        '阿银': "GinSan",
        "呱太": "Gekota",
        "黑子": "Kuroko",
        "神乐": "Kagura",
        "攘夷": "Jyoui",
        "攘夷战争": "Jyoui War",
        "婆婆": "Babaa",
        "登势婆婆": "OtoseBabaa",
        "登势": "Otose",
        "新八": "Shinpachi",
        "圣杯": "Holy Grail",
        "万事屋": "Yorozuya",
        "初春": "Oiharu",
    }
    for k, v in adhoc_translation.items():
        raw_translation[k] = v
    return raw_translation

def dict_to_text(dict):
    res=""
    for k, v in dict.items():
        for i in range(v):
            res += " " + k
    return res

def create_wordcloud_with_translation(name, text):
    """
    主函数：读取文件，分词，翻译，并生成带英文翻译的词云。
    """

    print("步骤 2: 使用 jieba 进行中文分词和过滤...")
    # 使用精确模式分词，并过滤掉停用词和单个汉字
    stopwords = load_stopwords()
    adhocwords = load_adhocwords()
    add_words(adhocwords)
    
    words = [word for word in jieba.cut(text) if word not in stopwords and len(word.strip()) > 1]
    
    # 统计词频
    word_counts = Counter(words)

    # 获取频率最高的词
    top_words = word_counts.most_common(MAX_WORDS)
    top_chinese_words = [word[0] for word in top_words]

    print(f"步骤 3: 翻译前 {len(top_chinese_words)} 个高频词汇 (这可能需要一些时间)...")
    translations = {}
    for word in top_chinese_words:
        if word[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            translations[word] = ""
            continue
        try:
            # 使用 'bing' 翻译器，通常比较稳定
            # 注意：频繁请求可能导致IP被临时屏蔽
            translated_text = ts.translate_text(word, translator='bing', from_language='zh-CN', to_language='en')
            translations[word] = translated_text
            print(f"  {word} -> {translated_text}")
        except Exception as e:
            print(f"  翻译 '{word}' 时出错: {e}")
            translations[word] = ""  # 翻译失败则留空
    translations = remap_translation(translations)

    new_top_words = {}
    for item, value in dict(top_words).items():
        new_item = item + ' ' + translations.get(item, "")
        new_top_words[new_item] = value

    print(new_top_words)
    words_text = dict_to_text(new_top_words)
    with open(f"./words/{name}.txt", "w", encoding='utf-8') as f:
        f.write(words_text)


    print("步骤 4: 生成词云布局...")
    # 仅使用词频来生成布局，而不直接生成图像
    wc = WordCloud(
        font_path=FONT_PATH,
        width=WIDTH,
        height=HEIGHT,
        background_color=BACKGROUND_COLOR,
        max_words=MAX_WORDS,
        prefer_horizontal=0.95, # 尽量让词语水平排列
        # collocations=False to avoid grouping words
        collocations=False,
        colormap='winter',
        stopwords=stopwords
    ).generate_from_frequencies(dict(new_top_words))

    plt.imshow(wc)  # 展示词云图
    plt.axis('off')
    # plt.show()
    print('display success!')
    
    # 保存词云图片
    wc.to_file(f"./output/{name}.jpg")
    return

    print("步骤 5: 使用 Matplotlib 绘制自定义词云...")
    fig, ax = plt.subplots(figsize=(WIDTH / 100, HEIGHT / 100))
    ax.set_facecolor(BACKGROUND_COLOR)

    # 将坐标轴范围设置为词云的画布大小
    ax.set_xlim(0, wc.width)
    ax.set_ylim(0, wc.height)
    def convert_color_format(color_str):
        """将 'rgb(r, g, b)' 格式的颜色字符串转换为 matplotlib 接受的 (r/255, g/255, b/255) 元组格式。"""
        match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_str)
        if match:
            r, g, b = map(int, match.groups())
            return (r / 255.0, g / 255.0, b / 255.0)
        # 如果格式不匹配，返回一个默认颜色
        return 'black'
    # 遍历词云布局信息 (word, font_size, position, orientation, color)
    for word, font_size, position, orientation, color in wc.layout_:
        x, y = position[1], position[0] # position 是 (y, x) 格式
        color = convert_color_format(color)
        # 绘制中文词
        is_horizontal = orientation is None or orientation == 0
        rotation = 0 if is_horizontal else 90
        
        ax.text(x, y, word,
                fontsize=font_size,
                fontproperties={'fname': FONT_PATH}, # 必须指定字体
                color=color,
                ha='center',
                va='center',
                rotation=rotation)

        # 获取并绘制英文翻译
        english_word = translations.get(word, "")
        if english_word:
            # 英文使用较小的字体大小
            english_font_size = max(font_size * 0.3, 8)

            if is_horizontal:
                # 如果是水平词，将英文放在正下方
                offset_y = font_size * 0.45
                ax.text(x, y - offset_y, f"({english_word})",
                        fontsize=english_font_size,
                        color=color,
                        ha='center',
                        va='center')
            else:
                # 如果是垂直词，将英文放在右侧（保持水平以方便阅读）
                offset_x = font_size * 0.5
                ax.text(x + offset_x, y, f"({english_word})",
                        fontsize=english_font_size,
                        color=color,
                        ha='left',
                        va='center')

    # 关闭坐标轴显示
    ax.axis('off')
    plt.tight_layout(pad=0)
    
    # 保存并显示图像
    output_filename = "wordcloud_with_translation.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', pad_inches=0)
    print(f"\n词云已生成并保存为 '{output_filename}'")
    plt.show()

def work_with_batch():
    print("步骤 1: 读取并合并文本文件...")
    text = ""
    if not os.path.exists(DATA_DIR):
        print(f"错误: 目录 '{DATA_DIR}' 不存在。请创建该目录并放入您的 .txt 文件。")
        return

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            # if filename != "saber.txt":
            #     continue
            file_path = os.path.join(DATA_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    create_wordcloud_with_translation(filename.replace(".txt", ""), text)
            except Exception as e:
                print(f"读取文件 {filename} 失败: {e}")
    
    if not text:
        print("错误: 未能在 data 目录中找到任何文本内容。")
        return

if __name__ == '__main__':
    work_with_batch()