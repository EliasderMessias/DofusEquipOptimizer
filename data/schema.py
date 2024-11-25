from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column, exc
from typing import List, Optional, Dict, Any

class BaseModel():
    def __repr__(self) -> str:
        return self._repr(id=self.id)

    def _repr(self, **fields: Dict[str, Any]) -> str:
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"
    
Base = declarative_base()

class Equipment(Base, BaseModel):
    __tablename__ = 'equipment'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column()
    level: Mapped[int] = mapped_column()
    type : Mapped[str] = mapped_column()

    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'equipment'}

    conditions: Mapped[Optional['Condition_Tree']] = relationship('Condition_Tree', back_populates = 'equipment')

    combat_effect: Mapped[Optional[str]] = mapped_column()
    stats: Mapped[List['Effect']] = relationship('Effect', back_populates = 'equipment')

    set_id: Mapped[Optional[int]] = mapped_column(ForeignKey('set.id'))
    parent_set: Mapped[Optional['Set']] = relationship('Set', back_populates = 'equipment') 

class Weapon(Equipment):
    __tablename__ = 'weapon'
    id: Mapped[int] = mapped_column(ForeignKey('equipment.id'), primary_key = True)
    attack_effect: Mapped[List['Effect']] = relationship('Effect', back_populates = 'weapon')
    criticalchance: Mapped[int] = mapped_column()
    critical_effect: Mapped[Optional[int]] = mapped_column()
    attack_cost: Mapped[int] = mapped_column()
    hits_per_turn: Mapped[int] = mapped_column()
    range_min: Mapped[int] = mapped_column()
    range_max: Mapped[int] = mapped_column()

    __mapper_args__ = {'polymorphic_identity': 'weapon'}

class Effect(Base):
    __tablename__ = 'effect'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column()
    int_maximum: Mapped[Optional[int]] = mapped_column()
    int_minimum: Mapped[int] = mapped_column()
    
class Condition_Tree(Base):
    __tablename__ = 'condition_tree'
    id: Mapped[int] = mapped_column(primary_key = True)
    condition: Mapped[Optional['Condition_Effect']] = relationship('Condition_Effect', back_populates = 'condition_tree')
       
    logic: Mapped[Optional[str]] = mapped_column()  # "and" or "or"
    children: Mapped[Optional['Condition_Tree']] = relationship('Condition_Tree', cascade = 'all, delete-orphan', back_populates = 'condition_tree')

class Condition_Effect(Base):
    __tablename__ = 'condition_effect'
    id: Mapped[int] = mapped_column(primary_key = True)
    relation: Mapped[str] = mapped_column()
    characteristic: Mapped[str] = mapped_column()
    value: Mapped[int] = mapped_column()

class Set(Base):
    __tablename__ = 'set'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column()
    
    items: Mapped[List['Equipment']] = relationship('Equipment', back_populates = 'set')

    set_bonus: Mapped[Dict[(int,'Set_Effect')]] = relationship('Set_Effect', back_populates = 'set') 

class Set_Effect(Base):
    __tablename__ = 'set_effect'
    id: Mapped[int] = mapped_column(primary_key = True)
    stats: Mapped[List['Effect']] = relationship('Effect', back_populates = 'set_effect')  
