from typing import List, Dict, Union, Any, Callable

from dataclass_dict_convert.convert import SimpleTypeConvertor


class ListConvertor(SimpleTypeConvertor):
    def __init__(self, element_convertor: SimpleTypeConvertor) -> None:
        super().__init__(List[element_convertor.type], None, None)
        self.element_convertor = element_convertor

    def convert_from_dict(self, val: Union[Dict, List, int, float, str, bool]) -> Any:
        return [self.element_convertor.convert_from_dict(item) for item in val]

    def convert_to_dict(self, val: Any) -> Union[Dict, List, int, float, str, bool]:
        return [self.element_convertor.convert_to_dict(item) for item in val]


class ForwardRefConvertor(SimpleTypeConvertor):
    def __init__(self, type) -> None:
        super().__init__(type, None, None)

    def convert_from_dict(self, val: Union[Dict, List, int, float, str, bool]) -> Any:
        return self.get_type().__forward_arg__.from_dict(val)

    def convert_to_dict(self, val: Any) -> Union[Dict, List, int, float, str, bool]:
        return self.get_type().__forward_arg__.to_dict(val)


class UnionConvertor(SimpleTypeConvertor):
    def __init__(self, type, mapping: Callable[[Union[Dict, List, int, float, str, bool]], Any]) -> None:
        super().__init__(type, None, None)
        self.types = type.__args__
        self.mapping = mapping

    def convert_from_dict(self, val: Union[Dict, List, int, float, str, bool]) -> Any:
        if not val: return None
        if isinstance(val, (int, float, str, bool, List)):
            return val

        return self.mapping(val)

    def convert_to_dict(self, val: Any) -> Union[Dict, List, int, float, str, bool]:
        if not val: return None
        for type in self.types:
            if isinstance(val, type): type.to_dict(val)
        return None


def ignore_unknown(field):
    pass


def ignore_fields(fields):
    return dict(
        custom_to_dict_convertors={
            field: lambda x: None
            for field in fields
        },
        custom_from_dict_convertors={
            field: lambda x: None
            for field in fields
        }
    )