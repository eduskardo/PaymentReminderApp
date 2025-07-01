from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.datepicker import DatePicker
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from datetime import datetime
import os

class PaymentReminderApp(App):
    def build(self):
        # Configuración inicial
        self.title = "Recordatorio de Pagos"
        self.store = JsonStore('payment_data.json')
        
        # Layout principal
        self.main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Título
        self.title_label = Label(text="Gestión de Pagos Mensuales", size_hint_y=None, height=50, font_size=24)
        self.main_layout.add_widget(self.title_label)
        
        # Formulario para agregar/editar pagos
        self.form_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=250)
        
        # Entidad
        self.entity_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.entity_layout.add_widget(Label(text="Entidad:", size_hint_x=0.3))
        self.entity_input = TextInput(multiline=False)
        self.entity_layout.add_widget(self.entity_input)
        self.form_layout.add_widget(self.entity_layout)
        
        # Descripción
        self.desc_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.desc_layout.add_widget(Label(text="Descripción:", size_hint_x=0.3))
        self.desc_input = TextInput(multiline=False)
        self.desc_layout.add_widget(self.desc_input)
        self.form_layout.add_widget(self.desc_layout)
        
        # Monto
        self.amount_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.amount_layout.add_widget(Label(text="Monto:", size_hint_x=0.3))
        self.amount_input = TextInput(multiline=False, input_filter='float')
        self.amount_layout.add_widget(self.amount_input)
        self.form_layout.add_widget(self.amount_layout)
        
        # Fecha de vencimiento
        self.date_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.date_layout.add_widget(Label(text="Vencimiento:", size_hint_x=0.3))
        self.date_input = Button(text="Seleccionar fecha")
        self.date_input.bind(on_release=self.show_date_picker)
        self.date_layout.add_widget(self.date_input)
        self.form_layout.add_widget(self.date_layout)
        
        # Frecuencia
        self.freq_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.freq_layout.add_widget(Label(text="Frecuencia:", size_hint_x=0.3))
        self.freq_spinner = Spinner(
            text='Mensual',
            values=('Mensual', 'Bimestral', 'Trimestral', 'Semestral', 'Anual')
        )
        self.freq_layout.add_widget(self.freq_spinner)
        self.form_layout.add_widget(self.freq_layout)
        
        # Botones del formulario
        self.button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.save_button = Button(text="Guardar")
        self.save_button.bind(on_release=self.save_payment)
        self.button_layout.add_widget(self.save_button)
        
        self.clear_button = Button(text="Limpiar")
        self.clear_button.bind(on_release=self.clear_form)
        self.button_layout.add_widget(self.clear_button)
        
        self.form_layout.add_widget(self.button_layout)
        self.main_layout.add_widget(self.form_layout)
        
        # Lista de entidades
        self.entities_label = Label(text="Entidades Registradas:", size_hint_y=None, height=30)
        self.main_layout.add_widget(self.entities_label)
        
        self.entities_scroll = ScrollView()
        self.entities_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.entities_grid.bind(minimum_height=self.entities_grid.setter('height'))
        self.entities_scroll.add_widget(self.entities_grid)
        self.main_layout.add_widget(self.entities_scroll)
        
        # Cargar datos existentes
        self.load_entities()
        
        return self.main_layout
    
    def show_date_picker(self, instance):
        """Muestra el selector de fecha"""
        date_picker = DatePicker()
        date_picker.bind(on_cancel=self.dismiss_popup)
        date_picker.bind(on_select=self.set_date)
        
        self.popup = Popup(title="Seleccionar fecha de vencimiento", content=date_picker, size_hint=(0.8, 0.6))
        self.popup.open()
    
    def dismiss_popup(self, instance):
        """Cierra el popup"""
        self.popup.dismiss()
    
    def set_date(self, instance, value):
        """Establece la fecha seleccionada"""
        self.date_input.text = value.strftime('%d/%m/%Y')
        self.dismiss_popup(instance)
    
    def save_payment(self, instance):
        """Guarda un nuevo pago o edita uno existente"""
        entity = self.entity_input.text.strip()
        description = self.desc_input.text.strip()
        amount = self.amount_input.text.strip()
        due_date = self.date_input.text
        frequency = self.freq_spinner.text
        
        if not entity or not amount or due_date == "Seleccionar fecha":
            self.show_message("Error", "Debe completar todos los campos obligatorios")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            self.show_message("Error", "El monto debe ser un número válido")
            return
        
        payment_data = {
            'entity': entity,
            'description': description,
            'amount': amount,
            'due_date': due_date,
            'frequency': frequency,
            'payments': []
        }
        
        # Guardar en el almacenamiento
        self.store.put(entity, **payment_data)
        self.show_message("Éxito", f"Pago para {entity} guardado correctamente")
        self.clear_form()
        self.load_entities()
    
    def clear_form(self, instance=None):
        """Limpia el formulario"""
        self.entity_input.text = ""
        self.desc_input.text = ""
        self.amount_input.text = ""
        self.date_input.text = "Seleccionar fecha"
        self.freq_spinner.text = "Mensual"
    
    def load_entities(self):
        """Carga las entidades existentes"""
        self.entities_grid.clear_widgets()
        
        for key in self.store.keys():
            data = self.store.get(key)
            entity_btn = Button(
                text=f"{data['entity']} - Vence: {data['due_date']} - ${data['amount']}",
                size_hint_y=None,
                height=60
            )
            entity_btn.bind(on_release=lambda btn, key=key: self.show_entity_details(key))
            self.entities_grid.add_widget(entity_btn)
    
    def show_entity_details(self, entity_key):
        """Muestra los detalles y el historial de pagos de una entidad"""
        data = self.store.get(entity_key)
        
        # Layout del popup
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Información de la entidad
        info_layout = GridLayout(cols=2, spacing=5, size_hint_y=None, height=150)
        info_layout.add_widget(Label(text="Entidad:"))
        info_layout.add_widget(Label(text=data['entity']))
        info_layout.add_widget(Label(text="Descripción:"))
        info_layout.add_widget(Label(text=data['description']))
        info_layout.add_widget(Label(text="Monto:"))
        info_layout.add_widget(Label(text=f"${data['amount']}"))
        info_layout.add_widget(Label(text="Vencimiento:"))
        info_layout.add_widget(Label(text=data['due_date']))
        info_layout.add_widget(Label(text="Frecuencia:"))
        info_layout.add_widget(Label(text=data['frequency']))
        popup_layout.add_widget(info_layout)
        
        # Historial de pagos
        history_label = Label(text="Historial de Pagos:", size_hint_y=None, height=30)
        popup_layout.add_widget(history_label)
        
        history_scroll = ScrollView()
        history_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        history_grid.bind(minimum_height=history_grid.setter('height'))
        
        if not data['payments']:
            history_grid.add_widget(Label(text="No hay pagos registrados"))
        else:
            for payment in data['payments']:
                history_grid.add_widget(Label(
                    text=f"{payment['date']} - ${payment['amount']}",
                    size_hint_y=None,
                    height=40
                ))
        
        history_scroll.add_widget(history_grid)
        popup_layout.add_widget(history_scroll)
        
        # Formulario para registrar nuevo pago
        new_payment_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        new_payment_layout.add_widget(Label(text="Registrar pago:", size_hint_x=0.4))
        
        self.new_payment_amount = TextInput(text=str(data['amount']), multiline=False, input_filter='float', size_hint_x=0.3)
        new_payment_layout.add_widget(self.new_payment_amount)
        
        register_btn = Button(text="Registrar", size_hint_x=0.3)
        register_btn.bind(on_release=lambda x: self.register_payment(entity_key))
        new_payment_layout.add_widget(register_btn)
        
        popup_layout.add_widget(new_payment_layout)
        
        # Botones de acciones
        action_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        edit_btn = Button(text="Editar")
        edit_btn.bind(on_release=lambda x: self.edit_entity(entity_key))
        action_layout.add_widget(edit_btn)
        
        delete_btn = Button(text="Eliminar")
        delete_btn.bind(on_release=lambda x: self.delete_entity(entity_key))
        action_layout.add_widget(delete_btn)
        
        close_btn = Button(text="Cerrar")
        close_btn.bind(on_release=lambda x: self.details_popup.dismiss())
        action_layout.add_widget(close_btn)
        
        popup_layout.add_widget(action_layout)
        
        self.details_popup = Popup(title="Detalles del Pago", content=popup_layout, size_hint=(0.9, 0.8))
        self.details_popup.open()
    
    def register_payment(self, entity_key):
        """Registra un nuevo pago en el historial"""
        try:
            amount = float(self.new_payment_amount.text)
        except ValueError:
            self.show_message("Error", "El monto debe ser un número válido")
            return
        
        data = self.store.get(entity_key)
        payment_record = {
            'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'amount': amount
        }
        data['payments'].append(payment_record)
        self.store.put(entity_key, **data)
        
        self.show_message("Éxito", "Pago registrado correctamente")
        self.details_popup.dismiss()
        self.show_entity_details(entity_key)
    
    def edit_entity(self, entity_key):
        """Carga los datos de una entidad para editarlos"""
        data = self.store.get(entity_key)
        self.entity_input.text = data['entity']
        self.desc_input.text = data['description']
        self.amount_input.text = str(data['amount'])
        self.date_input.text = data['due_date']
        self.freq_spinner.text = data['frequency']
        
        self.details_popup.dismiss()
        self.show_message("Edición", f"Puede editar los datos de {data['entity']}")
    
    def delete_entity(self, entity_key):
        """Elimina una entidad"""
        self.store.delete(entity_key)
        self.details_popup.dismiss()
        self.show_message("Eliminado", f"Entidad {entity_key} eliminada")
        self.load_entities()
    
    def show_message(self, title, message):
        """Muestra un mensaje emergente"""
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    PaymentReminderApp().run()