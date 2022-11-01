import json
import random

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from django.utils import translation, timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.contrib import messages
from entertainment.football import play
from entertainment.football_for_db import const
from entertainment.football_for_db import play as db_play
from entertainment import models as ent_models
from nft import models as nft_models
# Create your views here.
from utils import care_set
from users import models as users_models


@login_required(login_url="users:login")
def get_player_data(request):
    if request.method == "GET" and request.GET.get('player_id'):
        try:
            pos = {
                'GK': ['GK'],
                'DEF': ['CB', 'LB', 'RB'],
                'MID': ['CM', 'LM', 'RM', 'CDM', 'CAM'],
                'ATK': ['ST', 'CF', 'LW', 'RW']
            }

            p_id = request.GET.get('player_id')
            NFT_obj = nft_models.NFTCard.objects.get(
                id=p_id
            )

            context = {
                "pos": pos[NFT_obj.nft_info.position.r_po],
                "NFT_obj": NFT_obj,
            }
            team_id = request.GET.get('u')
            f_p = None
            for_players = NFT_obj.for_player.all()
            if for_players.exists() and team_id != '' and team_id:
                for for_player in for_players:
                    if int(team_id) == int(for_player.user_formation.id):
                        f_p = for_player
                        break
                    else:
                        f_p = None

            context['for_player'] = f_p
            return render(request, "PC_220112ST/entertainment/ajax/player_obj.html", context)
        except Exception as e:
            return
    else:
        return


def load_players(request):
    if request.user.is_anonymous:
        return render(request, 'PC_220112ST/entertainment/login_box.html')

    if request.method == 'GET' and request.GET.get('page'):

        filter_level = request.GET.get('f_l') if request.GET.get('f_l') else 'All'
        filter_po = request.GET.get('f_p') if request.GET.get('f_p') else 'All'
        filter_part = request.GET.get('f_part') if request.GET.get('f_part') else 'All'


        pos = nft_models.NFTPosition.objects.all()
        rates = nft_models.NFTRate.objects.all()

        pos_v = pos.values('po')
        rates_v = rates.values('rate')
        po = 'All'
        level = 'All'
        q = Q(nft_owner=request.user) & Q(is_selling = False)
        for po_v in pos_v:
            if po_v['po'] == filter_po:
                po = po_v['po']
                break
        if po != 'All':
            q &= Q(nft_info__position__po__icontains=po)

        for rate_v in rates_v:
            if rate_v['rate'] == filter_level:
                level = rate_v['rate']
                break
        if level != 'All':
            q &= Q(nft_info__rate__rate__icontains=level)

        context = dict()
        if request.GET.get('u') != '':
            user_form = ent_models.SetFormation.objects.get(
                id=int(request.GET.get('u'))
            )
            players = ent_models.ForPlayer.objects.filter(
                user_formation=user_form
            )
            context['players'] = players

            if filter_part in ['Starter', 'Candidate']:
                if filter_part == 'Starter':
                    q &= Q(for_player__user_formation=user_form)
                else:
                    q &= ~Q(for_player__user_formation=user_form)

        NFT_list = nft_models.NFTCard.objects.filter(
            q
        ).order_by('-created')

        paginator = Paginator(NFT_list, 11)
        page_num = request.GET.get('page')
        if not page_num:
            page_num = 1
        obj_count = NFT_list.count()
        try:
            NFT_list = paginator.page(page_num)
        except PageNotAnInteger:
            NFT_list = paginator.page(1)
        except EmptyPage:
            NFT_list = paginator.page(paginator.num_pages)

        index = NFT_list.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 4 if index >= 4 else 0
        if index < 4:
            end_index = 7 - start_index
        else:
            end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = list(paginator.page_range[start_index:end_index])

        context['NFT_list'] = NFT_list
        context['page_range'] = page_range
        context['obj_count'] = obj_count
        context['pos'] = pos
        context['rates'] = rates

        context['filter_rate'] = filter_level
        context['filter_po'] = filter_po
        context['filter_part'] = filter_part

        return render(request, 'PC_220112ST/entertainment/ajax/player_load.html', context)


def test_load_players(request):
    if request.method == 'GET' and request.GET.get('page'):
        context = dict()
        if request.GET.get('u') != '':
            user_form = ent_models.SetFormation.objects.get(
                id=int(request.GET.get('u'))
            )
            players = ent_models.ForPlayer.objects.filter(
                user_formation=user_form
            )
            context['players'] = players
        user = users_models.User.objects.get(
            username='yang'
        )
        NFT_list = nft_models.NFTCard.objects.filter(
            nft_owner=user
        ).order_by('-created')

        paginator = Paginator(NFT_list, 11)
        page_num = request.GET.get('page')
        if not page_num:
            page_num = 1
        obj_count = NFT_list.count()
        try:
            NFT_list = paginator.page(page_num)
        except PageNotAnInteger:
            NFT_list = paginator.page(1)
        except EmptyPage:
            NFT_list = paginator.page(paginator.num_pages)

        index = NFT_list.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 4 if index >= 4 else 0
        if index < 4:
            end_index = 7 - start_index
        else:
            end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = list(paginator.page_range[start_index:end_index])

        context['NFT_list'] = NFT_list
        context['page_range'] = page_range
        context['obj_count'] = obj_count

        return render(request, 'PC_220112ST/entertainment/ajax/test_player_load.html', context)


def main(request):
    context = dict()

    last_round = ent_models.MetaGameRoundInfo.objects.first()
    context['last_round'] = last_round

    return render(request, "PC_220112ST/entertainment/ent_intro.html", context)

@login_required(login_url="users:login")
def match_view(request, round_id):
    try:
        match = ent_models.MetaGameRoundInfo.objects.get(
            id=round_id
        )
    except ObjectDoesNotExist:
        return redirect('entertainment:match_list')

    if not match.check_end_date or not match.check_start_date:
        return redirect('entertainment:match_list')
    teams = ent_models.AITeam.objects.all().order_by('diff')

    games = ent_models.MetaGame.objects.filter(
        match=match,
        team1__owner=request.user,
        team2__in=teams
    )

    context = {
        'match': match,
        'teams': teams,
        'games': games
    }

    try:
        user_game = ent_models.UserParticipationHistory.objects.get(
            user = request.user,
            match = match
        )
    except ObjectDoesNotExist:
        user_game = None
    context['user_game'] = user_game
    if request.method == 'POST':
        games = ent_models.MetaGame.objects.filter(
            match=match,
            team1__owner=request.user,
            is_end=False,
            game_data="",
        )
        if games.count() == 10:
            user_part, is_fallow = ent_models.UserParticipationHistory.objects.get_or_create(
                user=request.user,
                match=match,
            )
            return redirect('entertainment:match',match.id)
        else:
            return render(request, "PC_220112ST/entertainment/ent_match.html", context)

    return render(request, "PC_220112ST/entertainment/ent_match.html", context)


@login_required(login_url="users:login")
def match_detail_view(request, round_id, team_name):
    try:

        match = ent_models.MetaGameRoundInfo.objects.get(
            id=round_id
        )
        ai_team = ent_models.AITeam.objects.get(
            team__team_name=team_name
        )
        context = {
            'match': match,
            'ai_team': ai_team,
        }
        if request.method == "GET":
            formation = request.GET.get('formation')

            for_players = list()

            if formation:
                try:
                    team = ent_models.SetFormation.objects.get(
                        owner=request.user,
                        formation_name=formation
                    )

                    context['team'] = team
                except:
                    context['team'] = None
                formation = formation.replace('-', ' - ')
            else:
                try:
                    game = ent_models.MetaGame.objects.get(
                        match=match,

                        team1__owner=request.user,
                        team2=ai_team
                    )
                    context['game'] = game
                    context['team'] = game.team1
                    if not formation:
                        formation = game.team1.get_formation_name()
                except:
                    context['team'] = None
                    pass
            if context['team']:
                players = ent_models.ForPlayer.objects.filter(
                    user_formation=context['team']
                )

                for i, pl in enumerate(players):
                    pos = const.FORM[context['team'].formation_name]['L'][i]['coord']
                    for_players.append({
                        'player': pl,
                        'pos': {
                            'x': pos.get_p_x,
                            'y': pos.get_p_y,
                        }
                    })

            context['for_players'] = for_players
            context['formation'] = formation
            context['FORMS'] = const.FORMS
            return render(request, "PC_220112ST/entertainment/ent_match_detail.html", context)

        elif request.method == "POST":
            ai_team_id = int(request.POST.get('ai_id'))
            team_id = int(request.POST.get('team_id'))

            user_team = ent_models.SetFormation.objects.get(
                id=team_id,
                owner=request.user
            )

            if match.start_date <= timezone.now() <= match.end_date:
                game_data, is_fallow = ent_models.MetaGame.objects.get_or_create(
                    match=match,
                    team1__owner=request.user,
                    team2=ai_team
                )
                if is_fallow and game_data.is_can_fix is False:
                    messages.add_message(request, messages.WARNING, '참여할 수 없는 경기입니다.')
                else:
                    if game_data.team1 != user_team:
                        game_data.team1 = user_team
                        game_data.save()

                    return redirect('entertainment:match',match.id)
            else:
                messages.add_message(request, messages.WARNING, '참여할 수 없는 경기입니다.')
            return render(request, "PC_220112ST/entertainment/ent_match_detail.html",context)
    except Exception as e:
        return render()

@login_required(login_url="users:login")
def match_result_detail(request, match_id):
    context = dict()
    match = ent_models.MetaGameRoundInfo.objects.get(
        id=int(match_id),
        is_end=True,
    )
    user_game = ent_models.UserParticipationHistory.objects.get(
        user=request.user,
        match=match
    )
    rounds = ent_models.MetaGame.objects.filter(
        match=match,
        team1__owner=request.user
    )
    context['match'] = match
    context['user_game'] = user_game
    context['rounds'] = rounds

    return render(request, "PC_220112ST/entertainment/ent_result_detail.html", context)


def game_result(request, game_id):
    context = dict()

    game = ent_models.MetaGame.objects.get(
        id=game_id
    )
    user_players = ent_models.ForPlayer.objects.filter(
        user_formation=game.team1
    )
    ai_players = ent_models.AIPlayer.objects.filter(
        AI_formation=game.team2
    )
    user_part = ent_models.UserParticipationHistory.objects.get(
        match = game.match,
        user = game.team1.owner,
    )
    context['game'] = game
    context['user_players'] = user_players
    context['ai_players'] = ai_players
    context['game_data'] = json.loads(game.game_data)
    context['user_part'] = user_part

    return render(request, "PC_220112ST/entertainment/ent_match_result.html", context)


def start_meta_league(request):
    context = dict()
    user = users_models.User.objects.get(
        username='yang'
    )
    user_formation = ent_models.SetFormation.objects.get(
        owner=user,
        formation_name='3-5-2'
    )
    user_players = ent_models.ForPlayer.objects.filter(
        user_formation=user_formation
    )

    ai_teams = ent_models.AITeam.objects.filter(
        diff=1
    )

    ai_team = random.choice(ai_teams)
    ai_players = ent_models.AIPlayer.objects.filter(
        AI_formation=ai_team
    )

    context['user_players'] = user_players
    context['ai_players'] = ai_players

    if request.method == "POST":
        game = db_play.set_db_data(user_formation, ai_team)



        return JsonResponse({"result": True,
                             "Game": game[0]},
                            )

    return render(request, "PC_220112ST/entertainment/index.html", context)


def match_rank(request, match_id):
    context = dict()
    match = ent_models.MetaGameRoundInfo.objects.get(
        id=match_id
    )
    user_recodes = ent_models.UserParticipationHistory.objects.filter(
        match=match,
        match__is_end=True,
    ).order_by('rank')
    context['user_count'] = user_recodes.count()
    context['match'] = match

    paginator = Paginator(user_recodes, 10)
    page_num = request.GET.get('page')
    if not page_num:
        page_num = 1
    try:
        user_recodes = paginator.page(page_num)
    except PageNotAnInteger:
        user_recodes = paginator.page(1)
    except EmptyPage:
        user_recodes = paginator.page(paginator.num_pages)

    index = user_recodes.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 4 if index >= 4 else 0
    if index < 4:
        end_index = 7 - start_index
    else:
        end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = list(paginator.page_range[start_index:end_index])

    context['user_recodes'] = user_recodes
    context['page_range'] = page_range

    return render(request, "PC_220112ST/entertainment/ent_rank.html", context)