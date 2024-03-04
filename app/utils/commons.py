# -*- coding: utf-8 -*-
import threading
import time
from collections import OrderedDict
import functools
import collections

# 线程锁
lock = threading.RLock()

# 全局实例
INSTANCES = OrderedDict()


# 单例模式注解
def singleton(cls):
    # 创建字典用来保存类的实例对象
    global INSTANCES

    def _singleton(*args, **kwargs):
        # 先判断这个类有没有对象
        if cls not in INSTANCES:
            with lock:
                if cls not in INSTANCES:
                    INSTANCES[cls] = cls(*args, **kwargs)
                    pass
        # 将实例对象返回
        return INSTANCES[cls]

    return _singleton


# 重试装饰器
def retry(ExceptionToCheck, tries=3, delay=3, backoff=2, logger=None):
    """
    :param ExceptionToCheck: 需要捕获的异常
    :param tries: 重试次数
    :param delay: 延迟时间
    :param backoff: 延迟倍数
    :param logger: 日志对象
    """

    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = f"{str(e)}, {mdelay} 秒后重试 ..."
                    if logger:
                        logger.warn(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry

    return deco_retry

def ttl_lru(seconds = 60, maxsize = 128, typed = False):
    cache = collections.OrderedDict()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _remove_expired_entries()  # 在访问缓存之前删除过期条目
            nonlocal cache
            key = functools._make_key(args, kwargs, typed)
            if key in cache:
                cache.move_to_end(key)
                return cache[key][0]  # 仅返回值，而不是过期时间
            try:
                result = func(*args, **kwargs)
                cache[key] = (result, time.time() + seconds)  # 将结果与过期时间一起存储
                if len(cache) > maxsize:
                    cache.popitem(last=False)
                return result
            except Exception as e:
                raise e

        def _remove_expired_entries():
            nonlocal cache
            current_time = time.time()
            for key, (value, expiration_time) in list(cache.items()):
                if expiration_time < current_time:
                    cache.pop(key)

        def clear_cache():
            nonlocal cache
            cache.clear()

        def cache_remove(*args, **kwargs):
            nonlocal cache
            key = functools._make_key(args, kwargs, typed)
            if key in cache:
                cache.pop(key)

        def cache_replace(value, *args, **kwargs):
            nonlocal cache
            key = functools._make_key(args, kwargs, typed)
            cache[key] = value

        wrapper.clear_cache = clear_cache
        wrapper.cache_remove = cache_remove
        wrapper.cache_replace = cache_replace

        return wrapper

    return decorator