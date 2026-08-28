from django.core.cache import cache

BOOKS_CACHE_VERSION_KEY = "books.cache:version"

def invalidate_books_cache():
    version = cache.get(BOOKS_CACHE_VERSION_KEY,1)

    cache.set(
        BOOKS_CACHE_VERSION_KEY,
        version + 1,
        timeout=None
    )


# we created higher level cache in validation to use for user and admin