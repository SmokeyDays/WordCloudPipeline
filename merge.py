import matplotlib.pyplot as plt
import os
import cairosvg
import io
from PIL import Image

# --- 用户配置 ---

# 1. 设置包含 SVG 文件的文件夹路径
#    重要：请将 './my_svgs' 替换为你的文件夹的实际路径
SVG_FOLDER_PATH = './output/msyh' 

# 2. 按您期望的顺序，准确列出六个 SVG 文件的名称
SVG_FILENAMES = [
    "gintoki.svg",
    "gintoki-deepseek.svg",
    "gintoki-doubao.svg",
    "saber.svg",
    "saber-deepseek.svg",
    "saber-doubao.svg",
]

# 3. 为您的六张图片定义标题
#    重要：标题的顺序必须与上面的 SVG_FILENAMES 列表一一对应
CAPTIONS = [
    "Gintoki - Human",
    "Gintoki - DeepSeek",
    "Gintoki - Doubao",
    "Gintoki - Human",
    "Gintoki - DeepSeek",
    "Gintoki - Doubao",
]

# --- 脚本主程序 ---

# 检查列表长度是否为 6
if len(SVG_FILENAMES) != 6 or len(CAPTIONS) != 6:
    print("错误：请确保 SVG_FILENAMES 和 CAPTIONS 列表中都正好包含六个项目。")
    exit()

# 创建一个 2 行 3 列的子图网格
fig, axes = plt.subplots(2, 3, figsize=(15, 11)) # 稍微增加了高度以容纳下方的标题

# 将 2x3 的 axes 数组扁平化为一维数组，方便遍历
axes = axes.flatten()

# 遍历您指定的文件名列表并在子图上绘图
for i, (filename, caption) in enumerate(zip(SVG_FILENAMES, CAPTIONS)):
    ax = axes[i]
    try:
        # 构建完整的文件路径
        file_path = os.path.join(SVG_FOLDER_PATH, filename)
        
        # 在内存中将 SVG 转换为 PNG 数据
        png_data = cairosvg.svg2png(url=file_path)
        
        # 从 PNG 数据中读取图像
        image = Image.open(io.BytesIO(png_data))
        
        # 在对应的子图上显示图像
        ax.imshow(image)

        # --- 这是修改过的部分 ---
        # 使用 ax.text() 将标题（Caption）放置在图像下方
        # (0.5, -0.1) 表示在 x 轴中心，y 轴下方 10% 的位置
        # ha='center' 和 va='top' 用于精确定位文本
        # transform=ax.transAxes 表示坐标是相对于子图区域的
        ax.text(0.5, -0.08, caption, 
                ha='center', 
                va='top', 
                fontsize=14, 
                transform=ax.transAxes)

    except FileNotFoundError:
        print(f"错误：文件未找到 '{file_path}'")
        ax.text(0.5, 0.5, f"文件未找到:\n{filename}", ha='center', va='center', color='red')
        
    except Exception as e:
        print(f"处理文件 {filename} 时出错: {e}")
        ax.text(0.5, 0.5, f"无法加载\n{filename}", ha='center', va='center', color='red')
    
    finally:
        # 关闭坐标轴，使图像更简洁
        ax.axis('off')

# 调整整体布局，防止重叠，并为主标题留出空间
# subplots_adjust 用于微调，可以给底部留出更多空间
fig.subplots_adjust(top=0.92, bottom=0.08)
plt.tight_layout(h_pad=4, rect=[0, 0, 1, 0.95])


# 显示最终生成的图像
plt.show()

# --- 如果需要将结果保存为文件，请取消下面这行代码的注释 ---
final_image_path = 'combined.png'
fig.savefig(final_image_path, dpi=300, bbox_inches='tight')
# print(f"图像已保存至 {final_image_path}")