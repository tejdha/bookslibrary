from django.db.models.signals import post_save, post_delete,pre_save
from django.dispatch import receiver 

from .models import ActivityLog, Book, Action

@receiver(pre_save,sender=Book)
def track_book_changes(sender, instance, **kwargs):
    if instance.pk is None:
        return
    
    old_book = Book.objects.get(pk=instance.pk)


    changes = {}
    # fields  = Book._meta.get_fields()
    for field in Book._meta.get_fields():
        if not hasattr(field, "attname"):
            continue
            
        field_name = field.name
        old_value = getattr(old_book, field_name)
        new_value = getattr(instance, field_name)

        if hasattr(old_value, "name"):
            old_value = old_value.name

        if hasattr(new_value, "name"):
            new_value = new_value.name

        if old_value != new_value:
            changes[field_name]={
                "old" : old_value,
                "new" : new_value
            }
    instance._changes = changes
    


@receiver(post_save, sender=Book)
# instance = new book(it has the books details which gave during creation) 
def book_created(sender, instance, created, **kwargs):
    if created: 

        # predelte what will be do with it
        ActivityLog.objects.create(
            user=instance.uploaded_by,
            action=Action.CREATED,
            book=instance.title,
            changes={},
        )
    else:      

        ActivityLog.objects.create(
            user=instance.uploaded_by,
            action=Action.UPDATED,
            book=instance.title,
            changes=getattr(instance, "_changes", {})
        )

@receiver(post_delete, sender=Book)
def book_deleted(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user = instance.uploaded_by,
        action= Action.DELETED,
        book=instance.title,
    )
    
        

