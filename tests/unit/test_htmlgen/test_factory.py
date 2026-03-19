"""Tests for HTMLGeneratorFactory."""


def test_factory_create_returns_article_html_generator():
    from capcat.htmlgen import HTMLGeneratorFactory, ArticleHTMLGenerator
    result = HTMLGeneratorFactory.create()
    assert isinstance(result, ArticleHTMLGenerator)


def test_factory_create_returns_new_instance_each_call():
    from capcat.htmlgen import HTMLGeneratorFactory
    a = HTMLGeneratorFactory.create()
    b = HTMLGeneratorFactory.create()
    assert a is not b
