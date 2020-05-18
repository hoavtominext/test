from Csaplus24.models import Csaplus24Average
from django.db import migrations


def set_names_for_csaplus24avg(apps, schema_editor):
    shortened_name = [
        '変化に気付いて伝える',
        '考え方や価値観の理解',
        '相手に合わせた話し方',
        '相手の強みを伸ばす',
        '会話で結論を出す',
        '目的を持って会話する',
        '遮らずに最後まで聞く',
        '落ち着いて話をさせる',
        '話しやすい雰囲気',
        'うなずきやあいづち',
        '定期的に話す',
        '目標の進捗を話す',
        'タイムリーな返答',
        'ねぎらう',
        'まず相手の考えを尋ねる',
        '相手に考えさせる質問',
        '明確な提案・要望',
        'やる気にさせる提案要望',
        'フィードバックを求める',
        'フィードバックする',
        '目標達成の促進',
        '成功や成長の支援',
        '組織の方向性の共有',
        '相手の目標理解'
    ]
    index = 0
    for question in Csaplus24Average.objects.all().order_by('id'):
        question.name = shortened_name[index]
        index+=1
        question.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Csaplus24', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_names_for_csaplus24avg, migrations.RunPython.noop)
    ]
