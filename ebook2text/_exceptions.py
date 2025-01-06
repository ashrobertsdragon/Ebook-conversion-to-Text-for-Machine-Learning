class ImageSizeError(Exception):
    """
    Custom exception class for image size-related errors.
    """

    pass


class ImageTooSmallError(ImageSizeError):
    """
    Custom exception class for handling errors related to an image being too
    small.
    """

    pass


class ImageTooLargeError(ImageSizeError):
    """
    Custom exception class for handling errors related to an image being too
    large.
    """

    pass


class NoResponseError(Exception):
    pass


class EbookConversionError(Exception):
    pass


class EbookConversionError(EbookConversionError):
    pass


class PDFConversionError(EbookConversionError):
    pass


class DocxConversionError(EbookConversionError):
    pass
