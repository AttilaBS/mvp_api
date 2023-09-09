from pydantic import BaseModel


class PictureSchema(BaseModel):
    '''
        Define os formatos aceitos de uma imagem a ser persistida.
    '''
    #TODO