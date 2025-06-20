# Generated by Django 5.2.2 on 2025-06-15 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grammarquestion',
            name='difficulty',
            field=models.CharField(choices=[('beginner', '初級'), ('intermediate', '中級'), ('advanced', '上級')], default='intermediate', max_length=20, verbose_name='難易度'),
        ),
        migrations.AddField(
            model_name='listeningquestion',
            name='audio_text',
            field=models.TextField(default='Sample audio text', verbose_name='音声テキスト'),
        ),
        migrations.AddField(
            model_name='listeningquestion',
            name='choice_d',
            field=models.CharField(default='Default choice D', max_length=200, verbose_name='選択肢D'),
        ),
        migrations.AddField(
            model_name='listeningquestion',
            name='difficulty',
            field=models.CharField(choices=[('beginner', '初級'), ('intermediate', '中級'), ('advanced', '上級')], default='intermediate', max_length=20, verbose_name='難易度'),
        ),
        migrations.AddField(
            model_name='vocabulary',
            name='difficulty',
            field=models.CharField(choices=[('beginner', '初級'), ('intermediate', '中級'), ('advanced', '上級')], default='intermediate', max_length=20, verbose_name='難易度'),
        ),
        migrations.AddField(
            model_name='vocabulary',
            name='pronunciation',
            field=models.CharField(blank=True, max_length=100, verbose_name='発音'),
        ),
        migrations.AlterField(
            model_name='grammarquestion',
            name='choice_d',
            field=models.CharField(default='Default choice D', max_length=200, verbose_name='選択肢D'),
        ),
        migrations.AlterField(
            model_name='listeningquestion',
            name='correct',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1, verbose_name='正解'),
        ),
        migrations.AlterField(
            model_name='listeningquestion',
            name='question',
            field=models.TextField(blank=True, verbose_name='問題文'),
        ),
    ]
