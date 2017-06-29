class Article:
    '''News Article'''
    def __init__(self, link, title=None, text=None, image=None):
        '''Initialise News Article

        `link` is the only required parameter,
        all others can be populated automatically by calling self.update
        when the object is initialised

        :param link: The url where the article should be located
        :type link: string
        :param title: The title of the article, defaults to None
        :type title: string, optional
        :param text: The message in the article, defaults to None
        :type text: string, optional
        :param image: A link to the main image in the article if one exists, defaults to None
        :type image: string, optional
        '''
        self.link = link
        if title is not None:
            self.title = title
        if text is not None:
            self.text = text
        if image is not None:
            self.image = image

    def __repr__(self):
        if self.title:
            return '<Article {}>'.format(self.title)
        else:
            return '<Article {}'.format(self.link)

    def __str__(self):
        if self.title is None:
            return self.link
        else:
            return self.title

    def update(self):
        pass
