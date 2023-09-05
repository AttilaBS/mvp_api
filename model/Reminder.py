class Reminder:

    def __init__(
        self,
        name:str,
        description:str, 
        interval:int,
        send_email:bool = False,
        recurring:bool = False,
        image:object = None):

        self.name = name,
        self.description = description,
        self.interval = interval,
        self.send_email = send_email,
        self.recurring = recurring,
        self.image = image
