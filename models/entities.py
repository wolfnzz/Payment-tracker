from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Counterparty(Base):
    """
    Таблица КОНТРАГЕНТЫ
    Содержит постоянные данные о поставщике.
    """
    __tablename__ = 'counterparties'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    invoices = relationship("Invoice", back_populates="counterparty", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.name}"


class Invoice(Base):
    """
    Таблица СЧЕТА
    Содержит данные по конкретным поставкам/оплатам.
    """
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True)

    # Связь с таблицей контрагентов
    counterparty_id = Column(Integer, ForeignKey('counterparties.id'), nullable=False)

    # Номер счета
    invoice_number = Column(String, nullable=False)

    # Сумма
    amount = Column(Float, nullable=False)

    # Срок платежа
    # храним количество дней отсрочки
    payment_term_days = Column(Integer, default=0)

    # Даты, необходимые для расчетов
    invoice_date = Column(Date, nullable=False)  # Дата выписки счета
    supply_date = Column(Date, nullable=False)  # Дата поставки (от нее считаем срок)

    # Статус оплаты
    is_paid = Column(Boolean, default=False)
    payment_date = Column(Date, nullable=True)  # Дата фактической оплаты (может быть пустой)

    # Связь таблиц
    counterparty = relationship("Counterparty", back_populates="invoices")

    @property
    def deadline_date(self):
        """
        Виртуальное поле: вычисляет конкретную дату, когда нужно платить.
        Логика: Дата поставки + Срок платежа (в днях).
        Используется для отображения в таблице и уведомлений.
        """
        from datetime import timedelta
        if self.supply_date and self.payment_term_days is not None:
            return self.supply_date + timedelta(days=self.payment_term_days)
        return self.supply_date

    def __repr__(self):
        return f"<Счет {self.invoice_number} на сумму {self.amount}>"
