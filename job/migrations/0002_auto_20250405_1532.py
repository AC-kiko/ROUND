# Generated by Django 3.2.8 on 2025-04-05 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobdata',
            options={'managed': True, 'verbose_name': '招聘信息', 'verbose_name_plural': '招聘信息'},
        ),
        migrations.AlterModelOptions(
            name='userlist',
            options={'managed': True, 'verbose_name': '前台用户', 'verbose_name_plural': '前台用户'},
        ),
        migrations.AddField(
            model_name='userlist',
            name='gpa',
            field=models.FloatField(blank=True, null=True, verbose_name='绩点'),
        ),
        migrations.AddField(
            model_name='userlist',
            name='grade',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='年级'),
        ),
        migrations.AddField(
            model_name='userlist',
            name='major',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='专业'),
        ),
        migrations.AddField(
            model_name='userlist',
            name='school',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='学校'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='company',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='公司名称'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='education',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='学历要求'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='experience',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='工作经验'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='href',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='职位链接'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='job_id',
            field=models.AutoField(primary_key=True, serialize=False, verbose_name='职位ID'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='key_word',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='关键词'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='label',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='职位标签'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='职位名称'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='place',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='工作地点'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='salary',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='薪资'),
        ),
        migrations.AlterField(
            model_name='jobdata',
            name='scale',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='公司规模'),
        ),
        migrations.AlterField(
            model_name='userlist',
            name='pass_word',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='密码'),
        ),
        migrations.AlterField(
            model_name='userlist',
            name='user_id',
            field=models.CharField(max_length=11, primary_key=True, serialize=False, verbose_name='用户ID'),
        ),
        migrations.AlterField(
            model_name='userlist',
            name='user_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='用户名'),
        ),
    ]
