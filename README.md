# fig_crawler

## Project 

simple python beauty pics crawler  

简单的python爬虫爬取图片【注意身体】

目前有下列风格
+ luyilu
+ feilin 
+ xiurenwang  秀人网
+ zhaifuli 宅福利
+ MiiTao 蜜桃社


## Installation

```python
pip install -r requirements.txt
```

## Param
```python
1. bianli_pages(func name): 主函数名称
2. offset(iter of ints): 偏移量，即各个引导页网址
3. fig_style(iter of ints): 图片风格ID，可迭代对象即可 
```

## Attention
运行时尽量填写较小的range范围， 默认的230差不多是整站的所有图片（耗时比较久）

## Future
+ 目前 urllib和requests 混用，后期全部改为requests
+ 加入代理（代理池是个问题）