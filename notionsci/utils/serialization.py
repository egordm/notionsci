import types
from typing import List, Dict, Union, Any, Callable, Optional, get_type_hints

from dataclass_dict_convert.convert import SimpleTypeConvertor, dataclass_dict_convert
from stringcase import camelcase, snakecase


class ExplicitNone():
    def __nonzero__(self):
        return False


class UndefinableMeta(type):
    def __getitem__(cls, key):
        new_cls = types.new_class(
            f"{cls.__name__}_{key.__name__}",
            (cls,),
            {},
            lambda ns: ns.__setitem__("type", Optional[key])
        )
        new_cls.__origin__ = Union
        new_cls.__args__ = [key, type(None)]  # , ExplicitNone]
        return new_cls


class Undefinable(metaclass=UndefinableMeta): pass


def serde(*, camel=False, ignore_unknown=False, **kwargs):
    case = camelcase if camel else snakecase

    def wrap(cls):
        types = get_type_hints(cls)
        undefinable_fields = [
            field_name
            for field_name, field_type in types.items()
            if isinstance(field_type, UndefinableMeta)
        ]

        cls = dataclass_dict_convert(
            dict_letter_case=case,
            on_unknown_field=ignore_unknown if ignore_unknown else None,
            **kwargs,
        )(cls)

        original_to_dict = cls.to_dict
        original_from_dict = cls.from_dict

        def to_dict(self, *args, **kwargs):
            result: dict = original_to_dict(self, *args, **kwargs)
            for field_name in undefinable_fields:
                field_name = case(field_name)
                if field_name in result and result[field_name] is None:
                    del result[field_name]
            return result

        def from_dict(dict, *args, **kwargs):
            result = original_from_dict(dict, *args, **kwargs)
            for field_name in undefinable_fields:
                field_name = case(field_name)
                if field_name in dict and dict[field_name] is None:
                    setattr(result, field_name, ExplicitNone())

            return result

        cls.to_dict = to_dict
        cls.from_dict = from_dict

        return cls

    return wrap


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


def list_from_dict(type, data: List[dict]) -> List[Any]:
    return [type.from_dict(x) for x in data]
