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
    
Base = declarative_base(cls=BaseModel)

class Equipment(Base):
    __tablename__ = 'equipment'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column()
    level: Mapped[int] = mapped_column()
    type : Mapped[str] = mapped_column()
    conditions: Mapped[Optional['Condition_Tree']] = relationship(uselist = False)
    combat_effect: Mapped[Optional[str]] = mapped_column()
    stats: Mapped[List['Effect']] = relationship('Effect')

    set_id: Mapped[int] = mapped_column(ForeignKey('set.id'))
    parent_set: Mapped[Optional['Set']] = relationship('Set', back_populates = 'items') 

    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'equipment'}

class Weapon(Equipment):
    __tablename__ = 'weapon'
    id: Mapped[int] = mapped_column(ForeignKey('equipment.id'), primary_key = True)
    attack_effect: Mapped[List['Effect']] = relationship('Effect', foreign_keys='Effect.equipment_id')
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
    equipment_id: Mapped[Optional[int]] = mapped_column(ForeignKey('equipment.id'))
    set_id: Mapped[Optional[int]] = mapped_column(ForeignKey('set_effect.set_id'))
    name: Mapped[str] = mapped_column()
    int_maximum: Mapped[Optional[int]] = mapped_column()
    int_minimum: Mapped[int] = mapped_column()
    
    def __repr__(self):
        return self._repr(id = self.id, name = self.name, max = self.int_maximum, min = self.int_minimum)


class Condition_Tree(Base):
    __tablename__ = 'condition_tree'
    id: Mapped[int] = mapped_column(primary_key = True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey('equipment.id')) 
    logic: Mapped[Optional[str]] = mapped_column()  # "and" or "or"
    condition: Mapped[Optional['Condition_Effect']] = relationship('Condition_Effect')    
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('condition_tree.id'))
    children: Mapped[Optional['Condition_Tree']] = relationship('Condition_Tree', cascade = 'all, delete-orphan')

class Condition_Effect(Base):
    __tablename__ = 'condition_effect'
    id: Mapped[int] = mapped_column(primary_key = True)
    tree_node_id: Mapped[int] = mapped_column(ForeignKey('condition_tree.id'))
    relation: Mapped[str] = mapped_column()
    characteristic: Mapped[str] = mapped_column()
    value: Mapped[int] = mapped_column()

class Set(Base):
    __tablename__ = 'set'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column()
    items: Mapped[List['Equipment']] = relationship('Equipment', back_populates = 'parent_set')
    set_bonus: Mapped[List['Set_Effect']] = relationship('Set_Effect') 

class Set_Effect(Base):
    __tablename__ = 'set_effect'
    id: Mapped[int] = mapped_column(primary_key = True)
    set_id: Mapped[int] = mapped_column(ForeignKey('set.id'))
    stats: Mapped[List['Effect']] = relationship('Effect')  
